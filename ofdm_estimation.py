import math

# User Definable Vars
DSOccupiedSpectrum = 96
DSLowerBandEdge = 678
DSAvgModulationOrder = 12
DSGuardBand = 2
DSExcludedBand = 2

# Constants
DSNumFFTBlocks = 1
DSSamplingRate = 204.8
DSSubcarrierSpacing = 50
DSCyclicPrefix = 512
DSWindowing = 128
DSPilotDensity_M = 48
DSExcludedSubcarriers = 20
NCPModulationOrder = 6
numSymbolsPerProfile = 1
DSLDPC_FEC_CW = [16200, 14216, 1800, 168, 16] # [CWSize, Infobits, Parity, BCH, CWheader]

def calculate_parameters():
    DSUpperBandEdge = DSLowerBandEdge + DSOccupiedSpectrum
    DSNumFFTPoints = (DSSamplingRate * 1000) / DSSubcarrierSpacing
    DSSymbolPeriod_usec = 1000 / DSSubcarrierSpacing
    DSCyclicPrefix_usec = DSCyclicPrefix / DSSamplingRate
    DSActualSymbolPeriod_usec = DSSymbolPeriod_usec + DSCyclicPrefix_usec
    DSSymbolEfficiency = 100 * DSSymbolPeriod_usec / DSActualSymbolPeriod_usec
    DSModulatedSubcarriers = (DSOccupiedSpectrum - DSGuardBand - DSExcludedBand) * 1000 / DSSubcarrierSpacing

    DSNumPLCSubcarriers = 8 if DSSubcarrierSpacing == 50 else 16

    DSNumContPilots = min(max(8, math.ceil(DSPilotDensity_M * DSOccupiedSpectrum / 190)), 120) + 8
    DSNumScatteredPilots = math.ceil((DSModulatedSubcarriers - DSNumPLCSubcarriers) / 128)
    DSEffectiveSubcarriers = DSModulatedSubcarriers - (DSExcludedSubcarriers + DSNumPLCSubcarriers * DSNumFFTBlocks + DSNumContPilots + DSNumScatteredPilots)

    return DSActualSymbolPeriod_usec, DSEffectiveSubcarriers

def calculate_data_rate(DSActualSymbolPeriod_usec, DSEffectiveSubcarriers):
    NCPBitsperMB = 48
    SubcarriersPerNCPMB = NCPBitsperMB / NCPModulationOrder
    NumBitsinDataSubcarriers = DSEffectiveSubcarriers * DSAvgModulationOrder
    if numSymbolsPerProfile > 1:
        NumBitsinDataSubcarriers *= numSymbolsPerProfile

    NumFullCodewords = math.floor(NumBitsinDataSubcarriers / DSLDPC_FEC_CW[0])
    NumNCPMBs = NumFullCodewords + math.ceil(numSymbolsPerProfile)

    EstimateShortendedCWSize = ((numSymbolsPerProfile * DSEffectiveSubcarriers - ((NumNCPMBs + 1) * SubcarriersPerNCPMB)) * DSAvgModulationOrder) - (DSLDPC_FEC_CW[0] * NumFullCodewords)
    ShortendedCWData = max(0, EstimateShortendedCWSize - (DSLDPC_FEC_CW[2] - DSLDPC_FEC_CW[3] - DSLDPC_FEC_CW[4]))

    totalDataBits = (NumFullCodewords * DSLDPC_FEC_CW[1]) + ShortendedCWData
    RateacrossWholeChannelGbps = totalDataBits / (DSActualSymbolPeriod_usec * numSymbolsPerProfile * 1000)
    DSPHYEfficiency = RateacrossWholeChannelGbps * pow(10, 3) / DSOccupiedSpectrum

    return totalDataBits, RateacrossWholeChannelGbps, DSPHYEfficiency

def main():
    DSActualSymbolPeriod_usec, DSEffectiveSubcarriers = calculate_parameters()
    totalDataBits, RateacrossWholeChannelGbps, DSPHYEfficiency = calculate_data_rate(DSActualSymbolPeriod_usec, DSEffectiveSubcarriers)

    print(f"Total Data Bits: {totalDataBits}")
    print(f"Rate across Whole Channel [Gbps]: {RateacrossWholeChannelGbps}")
    print(f"Downstream PHY Efficiency: {DSPHYEfficiency}")

if __name__ == "__main__":
    main()

