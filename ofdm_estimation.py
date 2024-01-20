import math

# User-defined variables
ds_occupied_spectrum = 192      # BW of OFDM ch in MHz
ds_lower_band_edge = 678        # Start freq of OFDM Ch in MHz
ds_avg_modulation_order = 12    # Modulation order in bits
ds_subcarrier_spacing = 50      # Subcarrier spacking in kHz

# Constants - you can obvously adjust these, but they are de-emphasized
DS_SAMPLING_RATE = 204.8
DS_CYCLIC_PREFIX = 512
DS_NUM_PLC_SUBCARRIERS = 8
DS_GUARD_BAND = 2
DS_EXCLUDED_BAND = 2
DS_EXCLUDED_SUBCARRIERS = 20
DS_PILOT_DENSITY_M = 48
NCP_BITS_PER_MB = 48
NCP_MODULATION_ORDER = 6
NUM_SYMBOLS_PER_PROFILE = 1
LDPC_FEC_CW = [16200, 14216, 1800, 168, 16]  # [CWSize, Infobits, Parity, BCH, CWheader]

# Derived calculations
ds_modulated_subcarriers = (ds_occupied_spectrum - DS_GUARD_BAND - DS_EXCLUDED_BAND) * 1000 / ds_subcarrier_spacing
ds_symbol_period_usec = 1000 / ds_subcarrier_spacing
ds_actual_symbol_period_usec = ds_symbol_period_usec + (DS_CYCLIC_PREFIX / DS_SAMPLING_RATE)
ds_num_cont_pilots = min(max(8, math.ceil(DS_PILOT_DENSITY_M * ds_occupied_spectrum / 190)), 120) + 8
subcarriers_per_ncp_mb = NCP_BITS_PER_MB / NCP_MODULATION_ORDER

# Main calculations
ds_num_scattered_pilots = math.ceil((ds_modulated_subcarriers - DS_NUM_PLC_SUBCARRIERS) / 128)
ds_effective_subcarriers = ds_modulated_subcarriers - (DS_EXCLUDED_SUBCARRIERS + DS_NUM_PLC_SUBCARRIERS * NUM_SYMBOLS_PER_PROFILE + ds_num_cont_pilots + ds_num_scattered_pilots)
num_bits_in_data_subcarriers = ds_effective_subcarriers * ds_avg_modulation_order
num_full_codewords = math.floor(num_bits_in_data_subcarriers / LDPC_FEC_CW[0])
num_ncp_mbs = num_full_codewords + math.ceil(NUM_SYMBOLS_PER_PROFILE)

estimate_shortened_cw_size = ((NUM_SYMBOLS_PER_PROFILE * ds_effective_subcarriers - ((num_ncp_mbs + 1) * subcarriers_per_ncp_mb)) * ds_avg_modulation_order) - (LDPC_FEC_CW[0] * num_full_codewords)
shortened_cw_data = max(0, estimate_shortened_cw_size - (LDPC_FEC_CW[2] - LDPC_FEC_CW[3] - LDPC_FEC_CW[4]))

total_data_bits = (num_full_codewords * LDPC_FEC_CW[1]) + shortened_cw_data
rate_across_whole_channel_gbps = total_data_bits / (ds_actual_symbol_period_usec * NUM_SYMBOLS_PER_PROFILE * 1000)
ds_phy_efficiency = rate_across_whole_channel_gbps * 1e3 / ds_occupied_spectrum

# Output
print(f"Total Data Bits: {total_data_bits}")
print(f"Rate across Whole Channel [Gbps]: {rate_across_whole_channel_gbps}")
print(f"Downstream PHY Efficiency: {ds_phy_efficiency}")
