import math

# Minislot Patterns
minislot_patterns = [
    [1, 8, 0, 2, 2], [2, 8, 0, 4, 2], [3, 8, 0, 8, 2], [4, 8, 0, 16, 2], [5, 8, 0, 1, 1],
    [6, 8, 0, 2, 1], [7, 8, 0, 4, 1], [1, 8, 1, 4, 4], [2, 8, 1, 6, 4], [3, 8, 1, 10, 4],
    [4, 8, 1, 16, 4], [5, 8, 1, 2, 2], [6, 8, 1, 3, 2], [7, 8, 1, 5, 2], [8, 16, 0, 2, 2],
    [9, 16, 0, 4, 2], [10, 16, 0, 8, 2], [11, 16, 0, 16, 2], [12, 16, 0, 1, 1], [13, 16, 0, 2, 1],
    [14, 16, 0, 4, 1], [8, 16, 1, 4, 4], [9, 16, 1, 6, 4], [10, 16, 1, 10, 4], [11, 16, 1, 18, 4],
    [12, 16, 1, 2, 2], [13, 16, 1, 3, 2], [14, 16, 1, 5, 2]
]

def minislot_capacity(K, modulation_order, pattern_index):
    """
    Calculates the minislot capacity based on the given parameters.
    """
    Q = minislot_patterns[pattern_index][1]
    cp_modulation_order = max(modulation_order - 4, 1)
    subcarriers = K * Q - minislot_patterns[pattern_index][3] - minislot_patterns[pattern_index][4]
    ms_capacity = modulation_order * subcarriers + cp_modulation_order * minislot_patterns[pattern_index][4]
    return ms_capacity

def calculate_upstream_ofdma_capacity(
    start_frequency, end_frequency, modulation_order, us_sampling_rate, us_subcarrier_spacing,
    us_pilot_pattern, us_cyclic_prefix, us_minislot_symbols_k, us_num_cont_legacy,
    us_excluded_spectrum, us_guard_band, us_excluded_nbi, us_addnl_edge_minislot,
    us_num_grants_in_profile
):
    """
    Calculates the upstream OFDMA channel capacity based on the given parameters.
    """
    us_occupied_spectrum = end_frequency - start_frequency
    us_lower_band_edge = start_frequency
    us_upper_band_edge = end_frequency
    us_active_bw = us_occupied_spectrum - us_excluded_spectrum
    us_cyclic_prefix_usec = us_cyclic_prefix / us_sampling_rate
    us_num_fft_points = 1000 * us_sampling_rate / us_subcarrier_spacing
    us_symbol_period_usec = 1000 / us_subcarrier_spacing
    us_actual_symbol_period_usec = us_symbol_period_usec + us_cyclic_prefix_usec
    us_symbol_efficiency = 100 * us_symbol_period_usec / us_actual_symbol_period_usec
    us_frame_duration_usec = us_minislot_symbols_k * us_actual_symbol_period_usec

    if us_subcarrier_spacing == 25:
        us_minislot_subcarriers_q = 16
        k_nbi = 3
    else:
        us_minislot_subcarriers_q = 8
        k_nbi = 2

    us_total_subcarriers = 1000 * us_occupied_spectrum / us_subcarrier_spacing
    us_excluded_subcarriers = (1000 * (us_excluded_spectrum + us_guard_band) / us_subcarrier_spacing) + (us_excluded_nbi * k_nbi)
    us_num_of_excl_spectrum_gaps = us_excluded_nbi + us_num_cont_legacy
    us_actual_signal_subcarriers = us_total_subcarriers - us_excluded_subcarriers
    us_temp_num_minislots = math.floor(us_actual_signal_subcarriers / us_minislot_subcarriers_q)
    us_minislot_efficiency = (us_actual_signal_subcarriers - us_num_of_excl_spectrum_gaps * 4) / us_actual_signal_subcarriers
    us_num_minislots = round(us_minislot_efficiency * us_temp_num_minislots)
    us_num_of_edge_minislots = us_num_grants_in_profile + us_addnl_edge_minislot
    us_num_of_body_minislots = us_num_minislots - us_num_of_edge_minislots

    local_us_pilot_pattern = us_pilot_pattern - 1  # Convert from spec index to array index
    if us_minislot_subcarriers_q == 16:
        local_us_pilot_pattern = local_us_pilot_pattern + 7

    us_capacity = (
        (us_num_of_body_minislots * minislot_capacity(us_minislot_symbols_k, modulation_order, local_us_pilot_pattern)) +
        (us_num_of_edge_minislots * minislot_capacity(us_minislot_symbols_k, modulation_order, local_us_pilot_pattern + 7))
    )
    avg_minislot_capacity = us_capacity / us_num_minislots

    profile_rate_mbps = (us_capacity / (us_minislot_symbols_k * us_actual_symbol_period_usec))
    us_phy_efficiency = profile_rate_mbps / us_active_bw
    us_phy_efficiency_w_fec_time_overhead = us_phy_efficiency * get_cw_sizes_for_efficiency(us_capacity)[0] * (us_symbol_efficiency / 100)

    return us_phy_efficiency_w_fec_time_overhead, profile_rate_mbps

# NOTE: The get_cw_sizes_for_efficiency function is not provided in the document,
# TODO: Implement this in the future for increased optimization (by maybe 1% :)
def get_cw_sizes_for_efficiency(us_capacity):
    """
    Placeholder function for calculating the FEC efficiency.
    Nneed to implement this function based on the FEC codeword selection algorithm in the future
    """
    return 1.0, 1.0  # Placeholder return values

# User input
start_frequency = float(input("Enter the start frequency (MHz): "))
end_frequency = float(input("Enter the end frequency (MHz): "))
modulation_order = int(input("Enter the modulation order (2-12): "))

# Example usage
result = calculate_upstream_ofdma_capacity(
    start_frequency=start_frequency, end_frequency=end_frequency, modulation_order=modulation_order,
    us_sampling_rate=102.4, us_subcarrier_spacing=25, us_pilot_pattern=8, us_cyclic_prefix=192,
    us_minislot_symbols_k=36, us_num_cont_legacy=1, us_excluded_spectrum=0, us_guard_band=1,
    us_excluded_nbi=0, us_addnl_edge_minislot=0, us_num_grants_in_profile=38
)

print(f"Upstream PHY Efficiency (with FEC time overhead): {result[0]:.6f}")
print(f"Upstream Channel Capacity (Mbps): {result[1]:.6f}")