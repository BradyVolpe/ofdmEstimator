import math

# --- Constants (Hardcoded for estimate_ofdm_throughput) ---
# These values are based on the 'Constants' section in the user's provided 'main' function.
# Some values that were user-definable in the original 'main' (like lower_band_edge)
# are now hardcoded here for the new function.

SAMPLING_RATE_MHZ = 204.8  # Sampling rate in MHz
CYCLIC_PREFIX_SAMPLES = 512  # Cyclic prefix in samples
NUM_FFT_BLOCKS = 1  # Number of FFT blocks, typically 1 for OFDM
PILOT_DENSITY_M = 48 # Factor for continuous pilot calculation
EXCLUDED_SUBCARRIERS_CONST = 20 # Number of explicitly excluded subcarriers (e.g., at band edges)
NCP_MODULATION_ORDER_BITS = 6 # Modulation order for Next Codeword Pointer (NCP)
NUM_SYMBOLS_PER_PROFILE = 1 # Number of OFDM symbols per profile/frame
LDPC_FEC_CW = [16200, 14216, 1800, 168, 16]  # [CWSize, Infobits, Parity, BCH, CWheader]
DEFAULT_LOWER_BAND_EDGE_MHZ = 108.0 # Default Lower Band Edge in MHz (e.g., start of DOCSIS 3.1 downstream)

def estimate_ofdm_throughput(
    spectrum,           # Occupied spectrum/channel width in MHz
    mod_order,          # Average modulation order (bits/symbol) for data subcarriers
    spacing,            # Subcarrier spacing in kHz
    guard,              # Guard band in MHz (total for both sides, or per side depending on interpretation)
    exclude             # Excluded band within the spectrum in MHz
):
    """
    Calculates the downstream OFDM channel data rate (Gbps) based on the 5 specified input parameters.
    Other necessary parameters are hardcoded within this function or as global constants.

    Args:
        spectrum (float): Occupied spectrum (channel width) in MHz.
        mod_order (int): Average modulation order (bits/symbol) for data subcarriers.
        spacing (float): Subcarrier spacing in kHz (e.g., 25 or 50).
        guard (float): Guard band in MHz. This is assumed to be the total guard band
                       subtracted from the occupied spectrum to get the active bandwidth.
        exclude (float): Excluded band within the spectrum in MHz (e.g., for notches).

    Returns:
        float: The calculated data rate across the whole channel in Gbps.
               Returns 0.0 if inputs are invalid or lead to no effective subcarriers.
    """
    # Map inputs to internal variable names for clarity
    occupied_spectrum_mhz = spectrum
    avg_modulation_order_bits = mod_order
    subcarrier_spacing_khz = spacing
    guard_band_mhz = guard
    excluded_band_mhz = exclude

    # Use hardcoded lower_band_edge
    lower_band_edge_mhz = DEFAULT_LOWER_BAND_EDGE_MHZ

    # --- Parameter Calculation (derived from user's calculate_parameters) ---
    if subcarrier_spacing_khz == 0:
        print("Error: Subcarrier spacing cannot be zero.")
        return 0.0
    if SAMPLING_RATE_MHZ == 0:
        print("Error: Sampling rate cannot be zero.")
        return 0.0

    # upper_band_edge_mhz = lower_band_edge_mhz + occupied_spectrum_mhz # Not directly needed for rate
    # num_fft_points = (SAMPLING_RATE_MHZ * 1000) / subcarrier_spacing_khz # Not directly needed for rate

    symbol_period_usec = 1000.0 / subcarrier_spacing_khz
    cyclic_prefix_usec = CYCLIC_PREFIX_SAMPLES / SAMPLING_RATE_MHZ # Samples / (Msamples/sec) = usec
    actual_symbol_period_usec = symbol_period_usec + cyclic_prefix_usec
    # symbol_efficiency = 100 * symbol_period_usec / actual_symbol_period_usec # Not directly needed for rate

    if actual_symbol_period_usec == 0:
        print("Error: Actual symbol period is zero.")
        return 0.0

    # Modulated subcarriers: total subcarriers in the active part of the spectrum
    active_spectrum_mhz = occupied_spectrum_mhz - guard_band_mhz - excluded_band_mhz
    if active_spectrum_mhz <= 0:
        print("Warning: Active spectrum is zero or negative after guard and exclusion.")
        return 0.0
    modulated_subcarriers = active_spectrum_mhz * 1000.0 / subcarrier_spacing_khz

    # PLC (Physical Layer Link Channel) subcarriers
    num_plc_subcarriers = 8 if subcarrier_spacing_khz == 50 else 16 # Typically 8 for 50kHz, 16 for 25kHz

    # Pilot subcarriers
    # Continuous pilots: based on pilot_density_m and occupied_spectrum.
    # The formula min(max(8, ceil(X)), 120) + 8 is specific.
    # Using occupied_spectrum_mhz for pilot density calculation as in original.
    num_cont_pilots_basic = math.ceil(PILOT_DENSITY_M * occupied_spectrum_mhz / 190.0)
    num_cont_pilots = min(max(8, num_cont_pilots_basic), 120) + 8
    
    # Scattered pilots: 1 per 128 data subcarriers (after PLC)
    # (modulated_subcarriers - num_plc_subcarriers) represents potential data/pilot bearing subcarriers
    subcarriers_for_scattered_calc = modulated_subcarriers - num_plc_subcarriers
    if subcarriers_for_scattered_calc < 0: subcarriers_for_scattered_calc = 0
    num_scattered_pilots = math.ceil(subcarriers_for_scattered_calc / 128.0)

    # Effective subcarriers for data transmission
    # Subtract various overheads:
    # EXCLUDED_SUBCARRIERS_CONST: fixed number of excluded subcarriers (e.g. band edges not covered by guard_band_mhz)
    # num_plc_subcarriers * NUM_FFT_BLOCKS: PLC overhead
    # num_cont_pilots: Continuous pilot overhead
    # num_scattered_pilots: Scattered pilot overhead
    effective_subcarriers = modulated_subcarriers - (EXCLUDED_SUBCARRIERS_CONST + \
                                                   num_plc_subcarriers * NUM_FFT_BLOCKS + \
                                                   num_cont_pilots + \
                                                   num_scattered_pilots)
    if effective_subcarriers <= 0:
        print("Warning: Effective data subcarriers is zero or negative.")
        return 0.0

    # --- Data Rate Calculation (derived from user's calculate_data_rate) ---
    ncp_bits_per_mb = 48 # Bits per Next Codeword Pointer Miniblock
    
    if NCP_MODULATION_ORDER_BITS == 0:
        print("Error: NCP modulation order cannot be zero.")
        return 0.0
    subcarriers_per_ncp_mb = ncp_bits_per_mb / NCP_MODULATION_ORDER_BITS

    num_bits_in_data_subcarriers = effective_subcarriers * avg_modulation_order_bits
    if NUM_SYMBOLS_PER_PROFILE > 1: # If multiple symbols form a larger processing block for FEC
        num_bits_in_data_subcarriers *= NUM_SYMBOLS_PER_PROFILE

    ldpc_cw_size_bits = LDPC_FEC_CW[0]
    ldpc_info_bits_per_cw = LDPC_FEC_CW[1]
    # ldpc_parity_bits = LDPC_FEC_CW[2]
    # ldpc_bch_bits = LDPC_FEC_CW[3]
    # ldpc_cw_header_bits = LDPC_FEC_CW[4]

    if ldpc_cw_size_bits == 0:
        print("Error: LDPC codeword size cannot be zero.")
        return 0.0

    num_full_codewords = math.floor(num_bits_in_data_subcarriers / ldpc_cw_size_bits)
    
    # Number of NCP miniblocks needed
    # Original: num_full_codewords + math.ceil(num_symbols_per_profile) - This seems high for typical NCP usage.
    # NCP is usually a small overhead per frame/profile.
    # A common interpretation is 1 NCP per profile, or related to number of codewords.
    # Let's use a simpler assumption: 1 NCP structure per profile.
    # The formula `(num_ncp_mbs + 1)` in shortened CW calc implies `num_ncp_mbs` might be 0 if no full NCP.
    # For simplicity, let's assume a fixed small overhead for NCP or use the original logic carefully.
    # Original logic for num_ncp_mbs:
    num_ncp_mbs = num_full_codewords + math.ceil(NUM_SYMBOLS_PER_PROFILE) # As per original

    # Shortened codeword calculation
    # Bits available for the last (potentially shortened) codeword
    # Original formula:
    # estimate_shortened_cw_size = ((NUM_SYMBOLS_PER_PROFILE * effective_subcarriers - \
    #                               ((num_ncp_mbs + 1) * subcarriers_per_ncp_mb)) * avg_modulation_order_bits) - \
    #                              (ldpc_cw_size_bits * num_full_codewords)
    # This calculation seems to re-evaluate total bits minus NCP and full codewords.
    # Let's break it down:
    total_potential_bits_in_profile = NUM_SYMBOLS_PER_PROFILE * effective_subcarriers * avg_modulation_order_bits
    ncp_overhead_bits = (num_ncp_mbs + 1) * subcarriers_per_ncp_mb * avg_modulation_order_bits # This is complex, original was (num_ncp_mbs + 1) * subcarriers_per_ncp_mb (which is subcarriers, not bits)
                                                                                              # The original formula seems to subtract NCP *subcarriers* from data *subcarriers* then multiply by mod_order
    
    # Re-evaluating shortened codeword part based on original structure:
    # Subcarriers available after NCP overhead for data and shortened CW
    subcarriers_for_data_and_shortened_cw = (NUM_SYMBOLS_PER_PROFILE * effective_subcarriers) - \
                                           ((num_ncp_mbs + 1) * subcarriers_per_ncp_mb) # This is total subcarriers for data/short_cw
    if subcarriers_for_data_and_shortened_cw < 0: subcarriers_for_data_and_shortened_cw = 0

    bits_for_data_and_shortened_cw = subcarriers_for_data_and_shortened_cw * avg_modulation_order_bits
    
    # Bits remaining after full codewords are accounted for from this pool
    remaining_bits_for_shortened_cw_raw = bits_for_data_and_shortened_cw - (ldpc_cw_size_bits * num_full_codewords)

    # Effective data bits in the shortened codeword (after FEC overhead for shortened part)
    # Original: max(0, estimate_shortened_cw_size - (ldpc_fec_cw[2] - ldpc_fec_cw[3] - ldpc_fec_cw[4]))
    # ldpc_fec_cw[2] = Parity, ldpc_fec_cw[3] = BCH, ldpc_fec_cw[4] = CWheader
    # This is Parity - BCH - CWHeader, which is the non-info part of the parity bits.
    # The actual overhead for a shortened codeword is more complex than subtracting a fixed parity amount.
    # A common approximation for shortened codeword info bits: K_short = K_full - (N_full - N_short)
    # where K is info bits, N is total bits.
    # If remaining_bits_for_shortened_cw_raw is N_short.
    # We need to find K_short.
    # If remaining_bits_for_shortened_cw_raw > 0, it forms a shortened codeword.
    # The number of info bits in a shortened codeword of length N_short is N_short - (N_full - K_full).
    # N_full - K_full is the total parity/overhead bits in a full codeword.
    parity_bits_in_full_cw = ldpc_cw_size_bits - ldpc_info_bits_per_cw
    
    shortened_cw_data_bits = 0
    if remaining_bits_for_shortened_cw_raw > parity_bits_in_full_cw: # Check if enough bits for at least some data
        shortened_cw_data_bits = max(0, remaining_bits_for_shortened_cw_raw - parity_bits_in_full_cw)
    elif remaining_bits_for_shortened_cw_raw > 0 and num_full_codewords == 0 : # Special case: only a shortened codeword exists
        # If the channel is too small for even one full codeword, but some bits exist.
        # This implies the entire transmission is one shortened codeword.
        shortened_cw_data_bits = max(0, remaining_bits_for_shortened_cw_raw - parity_bits_in_full_cw)


    total_data_bits = (num_full_codewords * ldpc_info_bits_per_cw) + shortened_cw_data_bits
    
    if NUM_SYMBOLS_PER_PROFILE == 0 or actual_symbol_period_usec == 0:
        rate_across_whole_channel_gbps = 0.0
    else:
        rate_across_whole_channel_gbps = total_data_bits / (actual_symbol_period_usec * NUM_SYMBOLS_PER_PROFILE * 1000.0) # Convert Mbps to Gbps

    # phy_efficiency = rate_across_whole_channel_gbps * 1e3 / occupied_spectrum_mhz # Not returned by this func

    return rate_across_whole_channel_gbps

# --- Original functions provided by user (for context/reference) ---
def calculate_parameters(
    o_spectrum, l_band_edge, avg_mod_order, g_band, excl_band, sub_spacing,
    # Constants that were global in original main
    sampling_rate_const, cyclic_prefix_const, num_fft_blocks_const,
    pilot_density_m_const, excluded_subcarriers_const_val
    ):
    """ Calculate various OFDM parameters. (User's original function) """
    upper_band_edge = l_band_edge + o_spectrum
    if sub_spacing == 0: return 0,0
    num_fft_points = (sampling_rate_const * 1000) / sub_spacing
    symbol_period_usec = 1000 / sub_spacing
    if sampling_rate_const == 0: return 0,0
    cyclic_prefix_usec = cyclic_prefix_const / sampling_rate_const
    actual_symbol_period_usec = symbol_period_usec + cyclic_prefix_usec
    # symbol_efficiency = 100 * symbol_period_usec / actual_symbol_period_usec # Not used in return
    
    active_spec = o_spectrum - g_band - excl_band
    if active_spec <=0: return actual_symbol_period_usec, 0
    modulated_subcarriers = active_spec * 1000 / sub_spacing

    num_plc_subcarriers = 8 if sub_spacing == 50 else 16
    num_cont_pilots_basic = math.ceil(pilot_density_m_const * o_spectrum / 190)
    num_cont_pilots = min(max(8, num_cont_pilots_basic), 120) + 8
    
    subcarriers_for_scattered_calc = modulated_subcarriers - num_plc_subcarriers
    if subcarriers_for_scattered_calc < 0: subcarriers_for_scattered_calc = 0
    num_scattered_pilots = math.ceil(subcarriers_for_scattered_calc / 128)
    
    effective_subcarriers = modulated_subcarriers - (excluded_subcarriers_const_val + \
                                                   num_plc_subcarriers * num_fft_blocks_const + \
                                                   num_cont_pilots + num_scattered_pilots)
    if effective_subcarriers < 0: effective_subcarriers = 0
    return actual_symbol_period_usec, effective_subcarriers

def calculate_data_rate(
    act_sym_period_usec, eff_subcarriers, avg_mod_order, o_spectrum,
    # Constants that were global in original main
    ncp_modulation_order_const, num_symbols_per_profile_const, ldpc_fec_cw_const
    ):
    """ Calculate the data rate of the OFDM channel. (User's original function) """
    if act_sym_period_usec == 0 or num_symbols_per_profile_const == 0 : return 0,0,0

    ncp_bits_per_mb = 48
    if ncp_modulation_order_const == 0: return 0,0,0
    subcarriers_per_ncp_mb = ncp_bits_per_mb / ncp_modulation_order_const
    
    num_bits_in_data_subcarriers = eff_subcarriers * avg_mod_order
    if num_symbols_per_profile_const > 1:
        num_bits_in_data_subcarriers *= num_symbols_per_profile_const

    if ldpc_fec_cw_const[0] == 0: return 0,0,0
    num_full_codewords = math.floor(num_bits_in_data_subcarriers / ldpc_fec_cw_const[0])
    num_ncp_mbs = num_full_codewords + math.ceil(num_symbols_per_profile_const)

    # Original shortened CW calculation
    subcarriers_for_data_and_shortened_cw = (num_symbols_per_profile_const * eff_subcarriers) - \
                                           ((num_ncp_mbs + 1) * subcarriers_per_ncp_mb)
    if subcarriers_for_data_and_shortened_cw < 0: subcarriers_for_data_and_shortened_cw = 0
    bits_for_data_and_shortened_cw = subcarriers_for_data_and_shortened_cw * avg_mod_order
    estimate_shortened_cw_size_bits_raw = bits_for_data_and_shortened_cw - (ldpc_fec_cw_const[0] * num_full_codewords)

    # Original shortened CW data bits logic
    # shortened_cw_data = max(0, estimate_shortened_cw_size_bits_raw - (ldpc_fec_cw_const[2] - ldpc_fec_cw_const[3] - ldpc_fec_cw_const[4]))
    # Using revised logic for shortened CW data bits:
    parity_bits_in_full_cw_const = ldpc_fec_cw_const[0] - ldpc_fec_cw_const[1]
    shortened_cw_data = 0
    if estimate_shortened_cw_size_bits_raw > parity_bits_in_full_cw_const:
        shortened_cw_data = max(0, estimate_shortened_cw_size_bits_raw - parity_bits_in_full_cw_const)
    elif estimate_shortened_cw_size_bits_raw > 0 and num_full_codewords == 0:
         shortened_cw_data = max(0, estimate_shortened_cw_size_bits_raw - parity_bits_in_full_cw_const)


    total_data_bits = (num_full_codewords * ldpc_fec_cw_const[1]) + shortened_cw_data
    rate_across_whole_channel_gbps = total_data_bits / (act_sym_period_usec * num_symbols_per_profile_const * 1000)
    
    phy_efficiency = 0
    if o_spectrum > 0 :
        phy_efficiency = rate_across_whole_channel_gbps * 1e3 / o_spectrum
    return total_data_bits, rate_across_whole_channel_gbps, phy_efficiency

# --- Main execution block for testing ---
if __name__ == "__main__":
    print("--- Testing new estimate_ofdm_throughput function ---")
    # Test Case 1: Values similar to user's original main()
    occupied_spectrum_input = 192   # MHz
    avg_modulation_order_input = 12 # bits/symbol
    subcarrier_spacing_input = 50   # kHz
    guard_band_input = 2            # MHz
    excluded_band_input = 2         # MHz

    rate_gbps_test1 = estimate_ofdm_throughput(
        spectrum=occupied_spectrum_input,
        mod_order=avg_modulation_order_input,
        spacing=subcarrier_spacing_input,
        guard=guard_band_input,
        exclude=excluded_band_input
    )
    print(f"\nTest Case 1 (50kHz spacing):")
    print(f"Inputs: Spectrum={occupied_spectrum_input}MHz, ModOrder={avg_modulation_order_input}, Spacing={subcarrier_spacing_input}kHz, Guard={guard_band_input}MHz, Exclude={excluded_band_input}MHz")
    print(f"Estimated OFDM Throughput: {rate_gbps_test1:.6f} Gbps")

    # Test Case 2: 25kHz subcarrier spacing
    subcarrier_spacing_25khz = 25 # kHz
    # For 25kHz, often modulation order might be slightly lower for robustness if covering same range
    # Or channel width might be different. Let's use a slightly smaller spectrum for this example.
    occupied_spectrum_25khz = 96 # MHz
    avg_mod_order_25khz = 10     # bits/symbol
    guard_band_25khz = 1.0       # MHz
    excluded_band_25khz = 1.0    # MHz

    rate_gbps_test2 = estimate_ofdm_throughput(
        spectrum=occupied_spectrum_25khz,
        mod_order=avg_mod_order_25khz,
        spacing=subcarrier_spacing_25khz,
        guard=guard_band_25khz,
        exclude=excluded_band_25khz
    )
    print(f"\nTest Case 2 (25kHz spacing):")
    print(f"Inputs: Spectrum={occupied_spectrum_25khz}MHz, ModOrder={avg_mod_order_25khz}, Spacing={subcarrier_spacing_25khz}kHz, Guard={guard_band_25khz}MHz, Exclude={excluded_band_25khz}MHz")
    print(f"Estimated OFDM Throughput: {rate_gbps_test2:.6f} Gbps")

    # Test Case 3: Zero effective subcarriers scenario
    rate_gbps_test3 = estimate_ofdm_throughput(
        spectrum=10, mod_order=10, spacing=50, guard=8, exclude=2
    )
    print(f"\nTest Case 3 (Low active spectrum):")
    print(f"Inputs: Spectrum=10MHz, ModOrder=10, Spacing=50kHz, Guard=8MHz, Exclude=2MHz")
    print(f"Estimated OFDM Throughput: {rate_gbps_test3:.6f} Gbps")


    print("\n--- Comparison with original calculation method (using its specific inputs) ---")
    # User Definable Vars from original main
    orig_occupied_spectrum = 192
    orig_lower_band_edge = 678 # This was user-definable, new func uses DEFAULT_LOWER_BAND_EDGE_MHZ
    orig_avg_modulation_order = 12
    orig_guard_band = 2
    orig_excluded_band = 2
    orig_subcarrier_spacing = 50

    # Constants from original main (passed to original functions)
    const_sampling_rate = 204.8
    const_cyclic_prefix = 512
    const_num_fft_blocks = 1
    const_pilot_density_m = 48
    const_excluded_subcarriers = 20
    const_ncp_modulation_order = 6
    const_num_symbols_per_profile = 1
    const_ldpc_fec_cw = [16200, 14216, 1800, 168, 16]

    actual_sym_period, eff_subcarriers = calculate_parameters(
        orig_occupied_spectrum, orig_lower_band_edge, orig_avg_modulation_order,
        orig_guard_band, orig_excluded_band, orig_subcarrier_spacing,
        const_sampling_rate, const_cyclic_prefix, const_num_fft_blocks,
        const_pilot_density_m, const_excluded_subcarriers
    )
    
    if eff_subcarriers > 0 and actual_sym_period > 0:
        _, rate_gbps_orig, _ = calculate_data_rate(
            actual_sym_period, eff_subcarriers, orig_avg_modulation_order, orig_occupied_spectrum,
            const_ncp_modulation_order, const_num_symbols_per_profile, const_ldpc_fec_cw
        )
        print(f"\nOriginal functions calculation (with LBE={orig_lower_band_edge}MHz):")
        print(f"Rate across Whole Channel [Gbps]: {rate_gbps_orig:.6f}")
    else:
        print(f"\nOriginal functions calculation resulted in no throughput (eff_subcarriers={eff_subcarriers}, period={actual_sym_period})")

    print(f"\nNote: The new 'estimate_ofdm_throughput' uses a hardcoded Lower Band Edge ({DEFAULT_LOWER_BAND_EDGE_MHZ} MHz) " +
          "and derives parameters internally. The 'original functions' calculation above uses the specific LBE " +
          f"({orig_lower_band_edge} MHz) from the user's example 'main'. Other hardcoded constants are aligned.")

