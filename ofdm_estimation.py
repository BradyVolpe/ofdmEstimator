import math

def calculate_parameters(occupied_spectrum, lower_band_edge, avg_modulation_order, guard_band, excluded_band, subcarrier_spacing):
    """
    Calculate various OFDM parameters.
    """
    upper_band_edge = lower_band_edge + occupied_spectrum
    num_fft_points = (sampling_rate * 1000) / subcarrier_spacing
    symbol_period_usec = 1000 / subcarrier_spacing
    cyclic_prefix_usec = cyclic_prefix / sampling_rate
    actual_symbol_period_usec = symbol_period_usec + cyclic_prefix_usec
    symbol_efficiency = 100 * symbol_period_usec / actual_symbol_period_usec
    modulated_subcarriers = (occupied_spectrum - guard_band - excluded_band) * 1000 / subcarrier_spacing

    num_plc_subcarriers = 8 if subcarrier_spacing == 50 else 16

    num_cont_pilots = min(max(8, math.ceil(pilot_density_m * occupied_spectrum / 190)), 120) + 8
    num_scattered_pilots = math.ceil((modulated_subcarriers - num_plc_subcarriers) / 128)
    effective_subcarriers = modulated_subcarriers - (excluded_subcarriers + num_plc_subcarriers * num_fft_blocks + num_cont_pilots + num_scattered_pilots)

    return actual_symbol_period_usec, effective_subcarriers

def calculate_data_rate(actual_symbol_period_usec, effective_subcarriers, avg_modulation_order, occupied_spectrum):
    """
    Calculate the data rate of the OFDM channel.
    """
    ncp_bits_per_mb = 48
    subcarriers_per_ncp_mb = ncp_bits_per_mb / ncp_modulation_order
    num_bits_in_data_subcarriers = effective_subcarriers * avg_modulation_order
    if num_symbols_per_profile > 1:
        num_bits_in_data_subcarriers *= num_symbols_per_profile

    num_full_codewords = math.floor(num_bits_in_data_subcarriers / ldpc_fec_cw[0])
    num_ncp_mbs = num_full_codewords + math.ceil(num_symbols_per_profile)

    estimate_shortened_cw_size = ((num_symbols_per_profile * effective_subcarriers - ((num_ncp_mbs + 1) * subcarriers_per_ncp_mb)) * avg_modulation_order) - (ldpc_fec_cw[0] * num_full_codewords)
    shortened_cw_data = max(0, estimate_shortened_cw_size - (ldpc_fec_cw[2] - ldpc_fec_cw[3] - ldpc_fec_cw[4]))

    total_data_bits = (num_full_codewords * ldpc_fec_cw[1]) + shortened_cw_data
    rate_across_whole_channel_gbps = total_data_bits / (actual_symbol_period_usec * num_symbols_per_profile * 1000)
    phy_efficiency = rate_across_whole_channel_gbps * 1e3 / occupied_spectrum

    return total_data_bits, rate_across_whole_channel_gbps, phy_efficiency

def main():
    # User Definable Vars
    occupied_spectrum = 192  # MHz
    lower_band_edge = 678   # MHz
    avg_modulation_order = 12
    guard_band = 2         # MHz
    excluded_band = 2      # MHz
    subcarrier_spacing = 50  # kHz

    # Constants
    global sampling_rate, cyclic_prefix, num_fft_blocks, pilot_density_m, excluded_subcarriers, ncp_modulation_order, num_symbols_per_profile, ldpc_fec_cw
    sampling_rate = 204.8  # MHz
    cyclic_prefix = 512
    num_fft_blocks = 1
    pilot_density_m = 48
    excluded_subcarriers = 20
    ncp_modulation_order = 6
    num_symbols_per_profile = 1
    ldpc_fec_cw = [16200, 14216, 1800, 168, 16]  # [CWSize, Infobits, Parity, BCH, CWheader]

    actual_symbol_period_usec, effective_subcarriers = calculate_parameters(occupied_spectrum, lower_band_edge, avg_modulation_order, guard_band, excluded_band, subcarrier_spacing)
    total_data_bits, rate_across_whole_channel_gbps, phy_efficiency = calculate_data_rate(actual_symbol_period_usec, effective_subcarriers, avg_modulation_order, occupied_spectrum)

    print(f"Total Data Bits: {total_data_bits}")
    print(f"Rate across Whole Channel [Gbps]: {rate_across_whole_channel_gbps}")
    print(f"Downstream PHY Efficiency: {phy_efficiency}")

if __name__ == "__main__":
    main()
