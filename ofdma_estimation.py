import math

# Minislot Patterns
# Each entry: [Pattern ID (for reference), Q (Subcarriers per Symbol in Minislot),
#              CP_flag (0 for no CP, 1 for CP), P (Pilots per K symbols without CP / Data Subcarriers with CP),
#              CP_overhead_subcarriers (Subcarriers used by CP per K symbols if CP_flag=1, or second type of pilot if CP_flag=0)]
# Index 0: Pattern ID (descriptive, not used in math)
# Index 1: Q (subcarriers per symbol in minislot, e.g., 8 for 50kHz, 16 for 25kHz)
# Index 2: CP_enabled_flag (0 or 1, indicates if pattern uses complimentary pilots)
# Index 3: Pilots_per_K_symbols_if_no_CP_OR_DataSubcarriers_with_CP (Meaning depends on CP_enabled_flag)
#          If CP_enabled_flag = 0, this is Number of Normal Pilot Subcarriers over K symbols.
#          If CP_enabled_flag = 1, this is (confusingly named in original data) Number of Data Subcarriers affected by CP over K symbols.
#                                   The actual DOCSIS spec refers to P_d and P_c for data and complimentary pilots.
#                                   The provided minislot_capacity formula seems to interpret pattern_data[3] as normal pilots
#                                   and pattern_data[4] as CP subcarriers. Let's stick to that interpretation.
# Index 4: CP_Subcarriers_per_K_symbols_if_CP_OR_SecondaryPilots_if_no_CP
#          If CP_enabled_flag = 0, this is Number of "Secondary/Boosted" Pilot Subcarriers over K symbols.
#          If CP_enabled_flag = 1, this is Number of Complimentary Pilot Subcarriers over K symbols.

minislot_patterns = [
    # For 50 kHz subcarrier spacing (Q=8)
    # Pattern ID, Q, CP_flag, Pilots_P, Pilots_CP/Secondary
    [1, 8, 0, 2, 2],  # P1 (index 0)
    [2, 8, 0, 4, 2],  # P2 (index 1)
    [3, 8, 0, 8, 2],  # P3 (index 2)
    [4, 8, 0, 16, 2], # P4 (index 3)
    [5, 8, 0, 1, 1],  # P5 (index 4)
    [6, 8, 0, 2, 1],  # P6 (index 5)
    [7, 8, 0, 4, 1],  # P7 (index 6)
    # For 50 kHz subcarrier spacing with Complimentary Pilots (Q=8)
    [1, 8, 1, 4, 4],  # P1_CP (index 7)
    [2, 8, 1, 6, 4],  # P2_CP (index 8)
    [3, 8, 1, 10, 4], # P3_CP (index 9)
    [4, 8, 1, 16, 4], # P4_CP (index 10)
    [5, 8, 1, 2, 2],  # P5_CP (index 11)
    [6, 8, 1, 3, 2],  # P6_CP (index 12)
    [7, 8, 1, 5, 2],  # P7_CP (index 13)
    # For 25 kHz subcarrier spacing (Q=16)
    [8, 16, 0, 2, 2],  # P8 (index 14)
    [9, 16, 0, 4, 2],  # P9 (index 15)
    [10, 16, 0, 8, 2], # P10 (index 16)
    [11, 16, 0, 16, 2],# P11 (index 17)
    [12, 16, 0, 1, 1], # P12 (index 18)
    [13, 16, 0, 2, 1], # P13 (index 19)
    [14, 16, 0, 4, 1], # P14 (index 20)
    # For 25 kHz subcarrier spacing with Complimentary Pilots (Q=16)
    [8, 16, 1, 4, 4],  # P8_CP (index 21)
    [9, 16, 1, 6, 4],  # P9_CP (index 22)
    [10, 16, 1, 10, 4],# P10_CP (index 23)
    [11, 16, 1, 18, 4],# P11_CP (index 24)
    [12, 16, 1, 2, 2], # P12_CP (index 25)
    [13, 16, 1, 3, 2], # P13_CP (index 26)
    [14, 16, 1, 5, 2]  # P14_CP (index 27)
]

def minislot_capacity(K_symbols, current_modulation_order, pattern_array_index):
    """
    Calculates the minislot capacity in bits based on the given parameters.
    K_symbols: Number of symbols per minislot (us_minislot_symbols_k).
    current_modulation_order: Bits per symbol for data subcarriers.
    pattern_array_index: 0-based index into the minislot_patterns array.
    """
    if not (0 <= pattern_array_index < len(minislot_patterns)):
        # Fallback to a default valid index if out of bounds
        print(f"Warning: pattern_array_index {pattern_array_index} is out of bounds. Defaulting to 0.")
        pattern_array_index = 0
        # raise ValueError(f"Pattern index {pattern_array_index} is out of bounds for minislot_patterns.")

    pattern_data = minislot_patterns[pattern_array_index]
    q_subcarriers_per_symbol = pattern_data[1]
    
    # Pilots interpretation based on common DOCSIS understanding:
    # pattern_data[3] = P_p (primary/normal pilots over K symbols)
    # pattern_data[4] = P_c (complimentary/secondary pilots over K symbols)
    num_primary_pilots_per_K_symbols = pattern_data[3]
    num_secondary_or_cp_pilots_per_K_symbols = pattern_data[4]

    cp_modulation_order = max(current_modulation_order - 4, 1)

    # Total "slots" for subcarriers over K symbols in a minislot
    total_subcarrier_slots_in_K_symbols = K_symbols * q_subcarriers_per_symbol
    
    # Total pilot subcarriers over K symbols
    total_pilot_subcarriers_in_K_symbols = num_primary_pilots_per_K_symbols + num_secondary_or_cp_pilots_per_K_symbols
    
    # Number of data-carrying subcarriers over K symbols
    data_carrying_subcarriers_in_K_symbols = total_subcarrier_slots_in_K_symbols - total_pilot_subcarriers_in_K_symbols
    
    # Capacity calculation based on user's original formula structure:
    # (mod_order * (K*Q - Pilots - CP_pilots)) + (cp_mod_order * CP_pilots)
    # This implies the first term is data on non-CP subcarriers, and second is data on CP subcarriers (if any)
    # If pattern_data[2] (CP_flag) is 0, then pattern_data[4] are secondary pilots, not CPs carrying data.
    # If pattern_data[2] (CP_flag) is 1, then pattern_data[4] are CP subcarriers that can carry data at cp_modulation_order.

    if pattern_data[2] == 1: # CP_enabled_flag is true
        # Data subcarriers are total minus primary pilots. CP subcarriers are separate.
        data_subcarriers = total_subcarrier_slots_in_K_symbols - num_primary_pilots_per_K_symbols - num_secondary_or_cp_pilots_per_K_symbols
        ms_capacity_bits = (current_modulation_order * data_subcarriers) + \
                           (cp_modulation_order * num_secondary_or_cp_pilots_per_K_symbols)
    else: # No CPs, so pattern_data[4] refers to secondary pilots (not carrying data)
        ms_capacity_bits = current_modulation_order * data_carrying_subcarriers_in_K_symbols
        
    return ms_capacity_bits


def estimate_ofdma_throughput(
    spectrum,           # Start frequency in MHz
    mod_order,          # Modulation order (bits/symbol)
    spacing,            # Subcarrier spacing in kHz
    guard,              # Guard band in MHz
    exclude             # Excluded spectrum in MHz
):
    """
    Calculates the upstream OFDMA channel capacity (profile rate in Mbps)
    based on the 5 specified input parameters. Other necessary parameters are hardcoded
    or derived internally.

    Args:
        spectrum (float): Start frequency of the OFDMA channel in MHz.
        mod_order (int): Modulation order (e.g., bits per symbol, like 10 for 1024-QAM).
        spacing (float): Subcarrier spacing in kHz (e.g., 25 or 50).
        guard (float): Guard band in MHz.
        exclude (float): Excluded spectrum in MHz.

    Returns:
        float: The calculated profile rate in Mbps.
    """
    # Map inputs to internal variable names with units for clarity
    spectrum_mhz = spectrum
    # mod_order is used directly
    spacing_khz = spacing
    guard_mhz = guard
    exclude_mhz = exclude

    # --- Hardcoded parameters ---
    # These values are based on the 'fixed_...' variables in the original script's __main__ block.
    # Some are made conditional on 'spacing_khz' for more realistic scenarios.

    default_channel_width_mhz_50khz = 32.0 # Typical for 50kHz spacing
    default_channel_width_mhz_25khz = 19.2 # Typical for 25kHz spacing (e.g. 960 subcarriers * 25kHz = 24MHz, less guard)
                                           # Or 6.4MHz, 12.8MHz, 19.2MHz, 25.6MHz are common widths.
    
    us_pilot_pattern_idx_50khz = 4   # 1-based (e.g., P4 for 50kHz, maps to array index 3)
    us_pilot_pattern_idx_25khz = 8   # 1-based (e.g., P8 for 25kHz, maps to array index 14 via 8-1+7)

    if spacing_khz == 25:
        derived_channel_width_mhz = default_channel_width_mhz_25khz
        us_pilot_pattern_idx = us_pilot_pattern_idx_25khz
        us_minislot_subcarriers_q = 16 # Subcarriers per symbol in a minislot for 25kHz
        k_nbi_factor = 3               # NBI exclusion factor for 25kHz
    else: # Default to 50kHz parameters
        derived_channel_width_mhz = default_channel_width_mhz_50khz
        us_pilot_pattern_idx = us_pilot_pattern_idx_50khz
        us_minislot_subcarriers_q = 8  # Subcarriers per symbol in a minislot for 50kHz
        k_nbi_factor = 2               # NBI exclusion factor for 50kHz

    end_frequency_mhz = spectrum_mhz + derived_channel_width_mhz
    
    # Other fixed parameters
    us_sampling_rate_msps = 102.4
    us_cyclic_prefix_samples = 192.0 # Use float for consistency in division
    us_minislot_symbols_k_val = 36
    us_num_cont_legacy_val = 1
    us_excluded_nbi_val = 0
    us_addnl_edge_minislot_val = 0
    us_num_grants_in_profile_val = 38 # This might also ideally vary with profile/channel width

    # --- Start of calculation logic (adapted from previous full-parameter version) ---
    us_occupied_spectrum_mhz = end_frequency_mhz - spectrum_mhz
    if us_occupied_spectrum_mhz <= 0:
        return 0.0

    if us_sampling_rate_msps == 0: return 0.0
    us_cyclic_prefix_usec = us_cyclic_prefix_samples / us_sampling_rate_msps
    
    if spacing_khz == 0: return 0.0
    us_symbol_period_usec = 1000.0 / spacing_khz
    
    us_actual_symbol_period_usec = us_symbol_period_usec + us_cyclic_prefix_usec
    if us_actual_symbol_period_usec == 0: return 0.0
        
    us_total_subcarriers = 1000.0 * us_occupied_spectrum_mhz / spacing_khz
    us_excluded_subcarriers_bands = 1000.0 * (exclude_mhz + guard_mhz) / spacing_khz
    us_excluded_subcarriers = us_excluded_subcarriers_bands + (us_excluded_nbi_val * k_nbi_factor)
    
    us_num_of_excl_spectrum_gaps = us_excluded_nbi_val + us_num_cont_legacy_val
    us_actual_signal_subcarriers = us_total_subcarriers - us_excluded_subcarriers

    if us_actual_signal_subcarriers <= 0: return 0.0

    us_temp_num_minislots = math.floor(us_actual_signal_subcarriers / us_minislot_subcarriers_q)
    
    if us_actual_signal_subcarriers == 0: us_minislot_efficiency = 0.0
    else:
        us_minislot_efficiency = (us_actual_signal_subcarriers - us_num_of_excl_spectrum_gaps * 4.0) / us_actual_signal_subcarriers
    
    us_num_minislots = round(us_minislot_efficiency * us_temp_num_minislots)
    if us_num_minislots <= 0: return 0.0

    us_num_of_edge_minislots = us_num_grants_in_profile_val + us_addnl_edge_minislot_val
    us_num_of_body_minislots = us_num_minislots - us_num_of_edge_minislots

    if us_num_of_body_minislots < 0:
        us_num_of_edge_minislots = us_num_minislots
        us_num_of_body_minislots = 0
    
    local_us_pilot_pattern_array_idx = us_pilot_pattern_idx - 1
    if us_minislot_subcarriers_q == 16: # For 25 kHz spacing
        local_us_pilot_pattern_array_idx = local_us_pilot_pattern_array_idx + 7

    body_minislot_pattern_idx = local_us_pilot_pattern_array_idx
    edge_minislot_pattern_idx = local_us_pilot_pattern_array_idx + 7 

    # Boundary checks for pattern indices (simplified)
    if not (0 <= body_minislot_pattern_idx < len(minislot_patterns)): body_minislot_pattern_idx = 0
    if not (0 <= edge_minislot_pattern_idx < len(minislot_patterns)): edge_minislot_pattern_idx = min(body_minislot_pattern_idx + 7, len(minislot_patterns)-1)


    us_capacity_bits = (
        (us_num_of_body_minislots * minislot_capacity(us_minislot_symbols_k_val, mod_order, body_minislot_pattern_idx)) +
        (us_num_of_edge_minislots * minislot_capacity(us_minislot_symbols_k_val, mod_order, edge_minislot_pattern_idx))
    )
    
    if us_minislot_symbols_k_val == 0 or us_actual_symbol_period_usec == 0:
        profile_rate_mbps = 0.0
    else:
        profile_rate_mbps = us_capacity_bits / (us_minislot_symbols_k_val * us_actual_symbol_period_usec)
    
    return profile_rate_mbps


def calculate_upstream_ofdma_capacity( # User's original function for comparison
    start_frequency, end_frequency, modulation_order, us_sampling_rate, us_subcarrier_spacing,
    us_pilot_pattern, us_cyclic_prefix, us_minislot_symbols_k, us_num_cont_legacy,
    us_excluded_spectrum, us_guard_band, us_excluded_nbi, us_addnl_edge_minislot,
    us_num_grants_in_profile
):
    us_occupied_spectrum = end_frequency - start_frequency
    us_active_bw = us_occupied_spectrum - us_excluded_spectrum 
    if us_sampling_rate == 0 or us_subcarrier_spacing == 0: return (0.0, 0.0)

    us_cyclic_prefix_usec = us_cyclic_prefix / us_sampling_rate
    us_symbol_period_usec = 1000.0 / us_subcarrier_spacing
    us_actual_symbol_period_usec = us_symbol_period_usec + us_cyclic_prefix_usec
    if us_actual_symbol_period_usec == 0: return (0.0, 0.0)

    us_symbol_efficiency = 100.0 * us_symbol_period_usec / us_actual_symbol_period_usec
    
    if us_subcarrier_spacing == 25:
        us_minislot_subcarriers_q = 16; k_nbi = 3
    else:
        us_minislot_subcarriers_q = 8; k_nbi = 2

    us_total_subcarriers = 1000.0 * us_occupied_spectrum / us_subcarrier_spacing
    us_excluded_subcarriers = (1000.0 * (us_excluded_spectrum + us_guard_band) / us_subcarrier_spacing) + (us_excluded_nbi * k_nbi)
    us_num_of_excl_spectrum_gaps = us_excluded_nbi + us_num_cont_legacy
    us_actual_signal_subcarriers = us_total_subcarriers - us_excluded_subcarriers
    if us_actual_signal_subcarriers <= 0: return (0.0, 0.0)

    us_temp_num_minislots = math.floor(us_actual_signal_subcarriers / us_minislot_subcarriers_q)
    if us_actual_signal_subcarriers == 0: us_minislot_efficiency = 0.0
    else: us_minislot_efficiency = (us_actual_signal_subcarriers - us_num_of_excl_spectrum_gaps * 4.0) / us_actual_signal_subcarriers
    us_num_minislots = round(us_minislot_efficiency * us_temp_num_minislots)
    if us_num_minislots <= 0: return (0.0, 0.0)

    us_num_of_edge_minislots = us_num_grants_in_profile + us_addnl_edge_minislot
    us_num_of_body_minislots = us_num_minislots - us_num_of_edge_minislots
    if us_num_of_body_minislots < 0:
        us_num_of_edge_minislots = us_num_minislots; us_num_of_body_minislots = 0

    local_us_pilot_pattern = us_pilot_pattern - 1 
    if us_minislot_subcarriers_q == 16: local_us_pilot_pattern += 7
    
    edge_pilot_pattern_idx = local_us_pilot_pattern + 7
    if not (0 <= local_us_pilot_pattern < len(minislot_patterns)): local_us_pilot_pattern = 0
    if not (0 <= edge_pilot_pattern_idx < len(minislot_patterns)): edge_pilot_pattern_idx = min(local_us_pilot_pattern + 7, len(minislot_patterns)-1)

    us_capacity = (
        (us_num_of_body_minislots * minislot_capacity(us_minislot_symbols_k, modulation_order, local_us_pilot_pattern)) +
        (us_num_of_edge_minislots * minislot_capacity(us_minislot_symbols_k, modulation_order, edge_pilot_pattern_idx))
    )

    if us_minislot_symbols_k == 0 or us_actual_symbol_period_usec == 0: profile_rate_mbps = 0.0
    else: profile_rate_mbps = us_capacity / (us_minislot_symbols_k * us_actual_symbol_period_usec)
    
    if us_active_bw == 0: us_phy_efficiency = 0.0
    else: us_phy_efficiency = profile_rate_mbps / us_active_bw

    fec_efficiency_factor, _ = get_cw_sizes_for_efficiency(us_capacity)
    us_phy_efficiency_w_fec_time_overhead = us_phy_efficiency * fec_efficiency_factor * (us_symbol_efficiency / 100.0)
    return us_phy_efficiency_w_fec_time_overhead, profile_rate_mbps

def get_cw_sizes_for_efficiency(us_capacity_bits):
    return 1.0, 1.0 

# --- Main script execution ---
if __name__ == "__main__":
    start_frequency_mhz_input = float(input("Enter the start frequency (MHz): "))
    # End frequency is still needed for the original comparison function
    end_frequency_mhz_input_for_original_calc = float(input("Enter the end frequency (MHz) (for original calculation comparison): "))
    modulation_order_input = int(input("Enter the modulation order (bits/symbol, e.g., 2-12): "))
    subcarrier_spacing_khz_input = float(input("Enter subcarrier spacing (kHz, e.g., 25 or 50): "))
    guard_band_mhz_input = float(input("Enter guard band (MHz): "))
    excluded_spectrum_mhz_input = float(input("Enter excluded spectrum (MHz): "))


    # Parameters for the original calculate_upstream_ofdma_capacity function
    # These are used to show a comparison or if that function is still needed elsewhere.
    # For a fair comparison, some of these would be the hardcoded ones in the new function.
    fixed_us_sampling_rate = 102.4
    fixed_us_pilot_pattern = 4 # This will be overridden by spacing in the new func
    if subcarrier_spacing_khz_input == 25:
        fixed_us_pilot_pattern = 8 # Match conditional logic in new func
        
    fixed_us_cyclic_prefix = 192
    fixed_us_minislot_symbols_k = 36
    fixed_us_num_cont_legacy = 1
    fixed_us_excluded_nbi = 0
    fixed_us_addnl_edge_minislot = 0
    fixed_us_num_grants_in_profile = 38

    print("\n--- Calling original calculate_upstream_ofdma_capacity function (for comparison) ---")
    # Note: end_frequency_mhz_input_for_original_calc is used here.
    # The new function will derive its own end_frequency.
    result_original_calc = calculate_upstream_ofdma_capacity(
        start_frequency=start_frequency_mhz_input,
        end_frequency=end_frequency_mhz_input_for_original_calc, # User supplied end_freq for this
        modulation_order=modulation_order_input,
        us_sampling_rate=fixed_us_sampling_rate,
        us_subcarrier_spacing=subcarrier_spacing_khz_input,
        us_pilot_pattern=fixed_us_pilot_pattern, # Matched to what new func would pick based on spacing
        us_cyclic_prefix=fixed_us_cyclic_prefix,
        us_minislot_symbols_k=fixed_us_minislot_symbols_k,
        us_num_cont_legacy=fixed_us_num_cont_legacy,
        us_excluded_spectrum=excluded_spectrum_mhz_input,
        us_guard_band=guard_band_mhz_input,
        us_excluded_nbi=fixed_us_excluded_nbi,
        us_addnl_edge_minislot=fixed_us_addnl_edge_minislot,
        us_num_grants_in_profile=fixed_us_num_grants_in_profile
    )
    if result_original_calc: # Check if not None
        print(f"Original Calc - Upstream PHY Efficiency (w FEC): {result_original_calc[0]:.6f}")
        print(f"Original Calc - Upstream Channel Capacity (Mbps): {result_original_calc[1]:.6f}")

    print("\n--- Calling new estimate_ofdma_throughput function (5 arguments) ---")
    # The new function uses hardcoded values for many parameters, including deriving end_frequency.
    profile_rate = estimate_ofdma_throughput(
        spectrum=start_frequency_mhz_input,
        mod_order=modulation_order_input,
        spacing=subcarrier_spacing_khz_input,
        guard=guard_band_mhz_input,
        exclude=excluded_spectrum_mhz_input
    )
    print(f"New Estimate (using derived end_freq & hardcoded params) - Profile Rate (Mbps): {profile_rate:.6f}")

    # Example: User inputs typical values for a 50kHz channel
    # Start: 10 MHz, End: 42 MHz (for original calc), Mod Order: 10, Spacing: 50, Guard: 0.8, Exclude: 0
    # New estimate_ofdma_throughput(10, 10, 50, 0.8, 0)
    #   - Internally, end_frequency will be 10 + 32.0 = 42.0 MHz
    #   - Pilot pattern will be 4 (P4)

    # Example: User inputs typical values for a 25kHz channel
    # Start: 10 MHz, End: 29.2 MHz (for original calc), Mod Order: 8, Spacing: 25, Guard: 0.4, Exclude: 0
    # New estimate_ofdma_throughput(10, 8, 25, 0.4, 0)
    #   - Internally, end_frequency will be 10 + 19.2 = 29.2 MHz
    #   - Pilot pattern will be 8 (P8)

