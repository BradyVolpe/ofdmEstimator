# OFDM Capacity Estimation

This software is designed to estimate the capacity of an Orthogonal Frequency-Division Multiplexing (OFDM) DOCSIS 3.1 channel. It calculates various parameters like the total data bits, the rate across the entire channel, and the Downstream Physical Layer (PHY) efficiency, based on user-defined input for the occupied spectrum, lower band edge, average modulation order, and subcarrier spacing.

## Author

Produced by Brady Volpe of The Volpe Firm, Inc.

## License

This project is licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. A copy of the License is included in this repository. 

You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

## Usage

The program requires Python 3.x to run. Set the essential variables at the beginning of the script as per your requirement:

- `occupied_spectrum`: The occupied spectrum in MHz, for example 192
- `lower_band_edge`: The lower band edge in MHz, for example 768
- `avg_modulation_order`: The average modulation order in 2's power, i.e. 2^12 = 4096-QAM
- `subcarrier_spacing`: The subcarrier spacing in kHz, for example 50

Run the script using a Python interpreter to get the OFDM capacity estimates.

## Contributions

Contributions are welcome. Please submit a pull request or open an issue for any enhancements, bug fixes, or feature requests.

## Contact

For more information or queries, please contact Brady Volpe at [brady [ at ] volpefirm dot com).
