# %%
import math
import copy

import Log
# %%
class Configuration_2_1_0:
  """reference to `MMWAVE SDK User Guide`

  MMWAVE SDK User Guide

  Product Release 2.1.0

  Release Date: Oct 5, 2018

  Document Version: 1.0

  Manufacturer: Texas Instruments Incorporated

  http://www.ti.com

  Currently only supports `xWR14xx`
  """
  __ProductRelease__ = '2.1.0'
  # logger:  Log.Logger | None = None
  # platform: str | None = None
  class Command:

    class SensorStart:
      """
        sensor Start command to RadarSS and datapath.
        Starts the sensor. This function triggers the transmission of the frames as per the frame and chirp configuration.
        By default, this function also sends the configuration to the mmWave Front End and the processing chain.
        This is a mandatory command.
      """
      Command = "sensorStart"
      Format= "{Command} {doReconfig}"
      def __init__(self):
        # Optionally, user can provide an argument 'doReconfig'
        #   1 - Do full reconfiguration of the device
        #   0 - Skip reconfiguration and just start the sensor using already provided configuration.
        self.doReconfig = None
      def parse(self, commandLine: str):
        parts: list[str] = commandLine.split(' ')
        if parts[0] == Configuration_2_1_0.Command.SensorStart.Command: 
          _ = parts.pop(0)
          if len(parts) == 1:
            self.doReconfig = int(parts.pop(0))
      @property
      def commandLine(self):
        return Configuration_2_1_0.Command.SensorStart.Format.format(
          Command = Configuration_2_1_0.Command.SensorStart.Command, 
          doReconfig = str(self.doReconfig) if self.doReconfig != None else ""
        )
    class FlushCfg:
      """
        This command should be issued after 'sensorStop' command to flush the old configuration and provide a new one.
        This is mandatory before any reconfiguration is performed post sensorStart.
      """
      Command = "flushCfg"
      Format= "{Command}"
      def __init__(self):
        pass
      def parse(self, commandLine: str):
        parts: list[str] = commandLine.split(' ')
        if parts[0] == Configuration_2_1_0.Command.FlushCfg.Command: 
          _ = parts.pop(0)
      @property
      def commandLine(self):
        return Configuration_2_1_0.Command.FlushCfg.Format.format(
          Command = Configuration_2_1_0.Command.FlushCfg.Command
        )
    class DfeDataOutputMode:
      """
        The values in this command should not change between sensorStop and sensorStart.
        Reboot the board to try config with different set of values in this command.
        This is a mandatory command.
      """
      Command = "dfeDataOutputMode"
      Format= "{Command} {modeType}"
      def __init__(self):
        # <modeType>
        #   1 - frame based chirps
        #   2 - continuous chirping
        #   3 - advanced frame config
        self.modeType = None
      def parse(self, commandLine: str):
        parts: list[str] = commandLine.split(' ')
        if parts[0] == Configuration_2_1_0.Command.DfeDataOutputMode.Command: 
          _ = parts.pop(0)
          if len(parts) == 1:
            self.modeType = int(parts.pop(0))
      @property
      def commandLine(self):
        return Configuration_2_1_0.Command.DfeDataOutputMode.Format.format(
          Command = Configuration_2_1_0.Command.DfeDataOutputMode.Command, 
          modeType = str(self.modeType) if self.modeType != None else ""
        )
    class ChannelCfg:
      """
        Channel config message to RadarSS. See mmwavelink doxgen for details.
        The values in this command should not change between sensorStop and sensorStart.
        Reboot the board to try config with different set of values in this command.
        This is a mandatory command.
      """
      Command = "channelCfg"
      Format= "{Command} {rxChannelEn} {txChannelEn} {cascading}"
      def __init__(self):
        # <rxChannelEn>
        #   Receive antenna mask e.g for 4 antennas, it is 0x1111b: 15
        self.rxChannelEn = None
        # <txChannelEn>
        #   Transmit antenna mask
        self.txChannelEn = None
        # <cascading>
        #   SoC cascading, not applicable, set to 0
        self.cascading = None
      def parse(self, commandLine: str):
        parts: list[str] = commandLine.split(' ')
        if parts[0] == Configuration_2_1_0.Command.ChannelCfg.Command: 
          _ = parts.pop(0)
          if len(parts) == 3:
            self.rxChannelEn = int(parts.pop(0))
            self.txChannelEn = int(parts.pop(0))
            self.cascading = int(parts.pop(0))
      @property
      def commandLine(self):
        return Configuration_2_1_0.Command.ChannelCfg.Format.format(
          Command = Configuration_2_1_0.Command.ChannelCfg.Command, 
          rxChannelEn = str(self.rxChannelEn) if self.rxChannelEn != None else "", 
          txChannelEn = str(self.txChannelEn) if self.txChannelEn != None else "", 
          cascading = str(self.cascading) if self.cascading != None else ""
        )
    class AdcCfg:
      """
        ADC config message to RadarSS. See mmwavelink doxgen for details.
        The values in this command should not change between sensorStop and sensorStart.
        Reboot the board to try config with different set of values in this command.
        This is a mandatory command.
      """
      Command = "adcCfg"
      Format= "{Command} {numADCBits} {adcOutputFmt}"
      def __init__(self):
        # <numADCBits>
        #   Number of ADC bits (0 for 12-bits, 1 for 14-bits and 2 for 16-bits)
        self.numADCBits = None
        # <adcOutputFmt>
        #   Output format :
        #     0 - real
        #     1 - complex 1x (image band filtered output)
        #     2 - complex 2x (image band visible)
        self.adcOutputFmt = None
      def parse(self, commandLine: str):
        parts: list[str] = commandLine.split(' ')
        if parts[0] == Configuration_2_1_0.Command.AdcCfg.Command: 
          _ = parts.pop(0)
          if len(parts) == 2:
            self.numADCBits = int(parts.pop(0))
            self.txChannelEn = int(parts.pop(0))
      @property
      def commandLine(self):
        return Configuration_2_1_0.Command.AdcCfg.Format.format(
          Command = Configuration_2_1_0.Command.AdcCfg.Command, 
          numADCBits = str(self.numADCBits) if self.numADCBits != None else "", 
          adcOutputFmt = str(self.adcOutputFmt) if self.adcOutputFmt != None else ""
        )
    class AdcbufCfg:
      """
        adcBuf hardware config. The values in this command can be changed between sensorStop and sensorStart.
        This is a mandatory command.
      """
      Command = "adcbufCfg"
      Format= "{Command} {subFrameIdx} {adcOutputFmt} {SampleSwap} {ChanInterleave} {ChirpThreshold}"
      def __init__(self):
        # <subFrameIdx>
        #   subframe Index (exists only in xwr16xx mmW demo)
        self.subFrameIdx = None
        # <adcOutputFmt>
        #   ADCBUF out format
        #     0 - Complex,
        #     1 - Real
        self.adcOutputFmt = None
        # <SampleSwap>
        #   ADCBUF IQ swap selection:
        #     0 - I in LSB, Q in MSB,
        #     1 - Q in LSB, I in MSB
        self.SampleSwap = None
        # <ChanInterleave>
        #   ADCBUF channel interleave configuration:
        #     0 - interleaved(not supported on XWR16xx),
        #     1 - non-interleaved
        self.ChanInterleave = None
        # <ChirpThreshold>
        #   Chirp Threshold configuration used for ADCBUF buffer to trigger ping/pong buffer switch.
        #   Valid values:
        #     0-8 for xWR16xx (conditions apply, see description in "Usage in mmW demo xwr16xx" column)
        #     only 1 for xWR14xx
        self.ChirpThreshold = None
      def parse(self, commandLine: str):
        parts: list[str] = commandLine.split(' ')
        if parts[0] == Configuration_2_1_0.Command.AdcbufCfg.Command: 
          _ = parts.pop(0)
          if len(parts) == 5:
            self.subFrameIdx = int(parts.pop(0))
          if len(parts) == 4:
            self.adcOutputFmt = int(parts.pop(0))
            self.SampleSwap = int(parts.pop(0))
            self.ChanInterleave = int(parts.pop(0))
            self.ChirpThreshold = int(parts.pop(0))
      @property
      def commandLine(self):
        return Configuration_2_1_0.Command.AdcbufCfg.Format.format(
          Command = Configuration_2_1_0.Command.AdcbufCfg.Command, 
          subFrameIdx = str(self.subFrameIdx) if self.subFrameIdx != None else "", 
          adcOutputFmt = str(self.adcOutputFmt) if self.adcOutputFmt != None else "", 
          SampleSwap = str(self.SampleSwap) if self.SampleSwap != None else "", 
          ChanInterleave = str(self.ChanInterleave) if self.ChanInterleave != None else "", 
          ChirpThreshold = str(self.ChirpThreshold) if self.ChirpThreshold != None else ""
        )
    class ProfileCfg:
      """
        Profile config message to RadarSS and datapath.
        See mmwavelink doxgen for details.
        The values in this command can be changed between sensorStop and sensorStart.
        This is a mandatory command.
      """
      Command = "profileCfg"
      Format= "{Command} {profileId} {startFreq} {idleTime} {adcStartTime} {rampEndTime} {txOutPower} {txPhaseShifter} {freqSlopeConst} {txStartTime} {numAdcSamples} {digOutSampleRate} {hpfCornerFreq1} {hpfCornerFreq2} {rxGain}"
      def __init__(self):
        # <profileId>
        #   profile Identifier
        self.profileId = None
        # <startFreq>
        #   "Frequency Start" in GHz (float values allowed)
        #   Examples:
        #     77
        #     78.1
        self.startFreq = None
        # <idleTime>
        #   "Idle Time" in u-sec (float values allowed)
        #   Examples:
        #     7
        #     7.15
        self.idleTime = None
        # <adcStartTime>
        #   "ADC Valid Start Time" in usec (float values allowed)
        #   Examples:
        #     7
        #     7.34
        self.adcStartTime = None
        # <rampEndTime>
        #   "Ramp End Time" in u-sec (float values allowed)
        #   Examples:
        #     58
        #     216.15
        self.rampEndTime = None
        # <txOutPower>
        #   Tx output power back-off code for tx antennas
        self.txOutPower = None
        # <txPhaseShifter>
        #   tx phase shifter for tx antennas
        self.txPhaseShifter = None
        # <freqSlopeConst>
        #   "Frequency slope" for the chirp in MHz/usec (float values allowed)
        #   Examples:
        #     68
        #     16.83
        self.freqSlopeConst = None
        # <txStartTime>
        #   "TX Start Time" in u-sec (float values allowed)
        #   Examples:
        #     1
        #     2.92
        self.txStartTime = None
        # <numAdcSamples>
        #   number of ADC samples collected during "ADC Sampling Time" as shown in the chirp diagram above.
        #   Examples:
        #     256
        #     224
        self.numAdcSamples = None
        # <digOutSampleRate>
        #   ADC sampling frequency in ksps.
        #   (<numAdcSamples> / <digOutSampleRate>: "ADC Sampling Time")
        #   Examples:
        #     5500
        self.digOutSampleRate = None
        # <hpfCornerFreq1>
        #   HPF1 (High Pass Filter 1) corner frequency
        #     0: 175 KHz
        #     1: 235 KHz
        #     2: 350 KHz
        #     3: 700 KHz
        self.hpfCornerFreq1 = None
        # <hpfCornerFreq2>
        #   HPF2 (High Pass Filter 2) corner frequency
        #     0: 350 KHz
        #     1: 700 KHz
        #     2: 1.4 MHz
        #     3: 2.8 MHz
        self.hpfCornerFreq2 = None
        # <rxGain>
        #   OR'ed value of RX gain in dB and RF gain target (See mmwavelink doxgen for details)
        self.rxGain = None
      def parse(self, commandLine: str):
        parts: list[str] = commandLine.split(' ')
        if parts[0] == Configuration_2_1_0.Command.ProfileCfg.Command: 
          _ = parts.pop(0)
          if len(parts) == 14:
            self.profileId = int(parts.pop(0))
            self.startFreq = float(parts.pop(0))
            self.idleTime = float(parts.pop(0))
            self.adcStartTime = float(parts.pop(0))
            self.rampEndTime = float(parts.pop(0))
            self.txOutPower = int(parts.pop(0))
            self.txPhaseShifter = int(parts.pop(0))
            self.freqSlopeConst = float(parts.pop(0))
            self.txStartTime = float(parts.pop(0))
            self.numAdcSamples = int(parts.pop(0))
            self.digOutSampleRate = int(parts.pop(0))
            self.hpfCornerFreq1 = int(parts.pop(0))
            self.hpfCornerFreq2 = int(parts.pop(0))
            self.rxGain = int(parts.pop(0))
      @property
      def commandLine(self):
        return Configuration_2_1_0.Command.ProfileCfg.Format.format(
          Command = Configuration_2_1_0.Command.ProfileCfg.Command, 
          profileId = str(self.profileId) if self.profileId != None else "", 
          startFreq = str(self.startFreq) if self.startFreq != None else "", 
          idleTime = str(self.idleTime) if self.idleTime != None else "", 
          adcStartTime = str(self.adcStartTime) if self.adcStartTime != None else "", 
          rampEndTime = str(self.rampEndTime) if self.rampEndTime != None else "", 
          txOutPower = str(self.txOutPower) if self.txOutPower != None else "", 
          txPhaseShifter = str(self.txPhaseShifter) if self.txPhaseShifter != None else "", 
          freqSlopeConst = str(self.freqSlopeConst) if self.freqSlopeConst != None else "", 
          txStartTime = str(self.txStartTime) if self.txStartTime != None else "", 
          numAdcSamples = str(self.numAdcSamples) if self.numAdcSamples != None else "", 
          digOutSampleRate = str(self.digOutSampleRate) if self.digOutSampleRate != None else "", 
          hpfCornerFreq1 = str(self.hpfCornerFreq1) if self.hpfCornerFreq1 != None else "", 
          hpfCornerFreq2 = str(self.hpfCornerFreq2) if self.hpfCornerFreq2 != None else "", 
          rxGain = str(self.rxGain) if self.rxGain != None else ""
        )
    class ChirpCfg: # muilt
      """
        Chirp config message to RadarSS and datapath.
        See mmwavelink doxgen for details.
        The values in this command can be changed between sensorStop and sensorStart.
        This is a mandatory command.
      """
      Command = "chirpCfg"
      Format= "{Command} {chirpStartIndex} {chirpEndIndex} {profileIdentifier} {startFrequencyVariation} {frequencySlopeVariation} {idleTimeVariation} {adcStartTimeVariation} {txAntennaEnableMask}"
      def __init__(self):
        # chirp start index
        self.chirpStartIndex = None
        # chirp end index
        self.chirpEndIndex = None
        # profile identifier
        self.profileIdentifier = None
        # start frequency variation in Hz (float values allowed)
        self.startFrequencyVariation = None
        # frequency slope variation in kHz/us (float values allowed)
        self.frequencySlopeVariation = None
        # idle time variation in u-sec (float values allowed)
        self.idleTimeVariation = None
        # ADC start time variation in usec (float values allowed)
        self.adcStartTimeVariation = None
        # tx antenna enable mask (Tx2,Tx1) e.g (10)b: Tx2 enabled, Tx1 disabled.
        self.txAntennaEnableMask = None
      def parse(self, commandLine: str):
        parts: list[str] = commandLine.split(' ')
        if parts[0] == Configuration_2_1_0.Command.ChirpCfg.Command: 
          _ = parts.pop(0)
          if len(parts) == 8:
            self.chirpStartIndex = int(parts.pop(0))
            self.chirpEndIndex = int(parts.pop(0))
            self.profileIdentifier = float(parts.pop(0))
            self.startFrequencyVariation = int(parts.pop(0))
            self.frequencySlopeVariation = float(parts.pop(0))
            self.idleTimeVariation = float(parts.pop(0))
            self.adcStartTimeVariation = float(parts.pop(0))
            self.txAntennaEnableMask = int(parts.pop(0))
      @property
      def commandLine(self):
        return Configuration_2_1_0.Command.ChirpCfg.Format.format(
          Command = Configuration_2_1_0.Command.ChirpCfg.Command, 
          chirpStartIndex = str(self.chirpStartIndex) if self.chirpStartIndex != None else "", 
          chirpEndIndex = str(self.chirpEndIndex) if self.chirpEndIndex != None else "", 
          profileIdentifier = str(self.profileIdentifier) if self.profileIdentifier != None else "", 
          startFrequencyVariation = str(self.startFrequencyVariation) if self.startFrequencyVariation != None else "", 
          frequencySlopeVariation = str(self.frequencySlopeVariation) if self.frequencySlopeVariation != None else "", 
          idleTimeVariation = str(self.idleTimeVariation) if self.idleTimeVariation != None else "", 
          adcStartTimeVariation = str(self.adcStartTimeVariation) if self.adcStartTimeVariation != None else "", 
          txAntennaEnableMask = str(self.txAntennaEnableMask) if self.txAntennaEnableMask != None else ""
        )
    class BpmCfg:
      """
        BPM MIMO configuration.
        Every frame consists of alternating chirps with pattern TX1_Tx2 and TX1-TX2. 
        This is alternate configuration to TDM-MIMO scheme and provides SNR improvement by running 2Tx simultaneously.
        When using this scheme, user should enable both the azimuth TX in the chirpCfg. 
        See profile_2d_bpm.cfg profile in the xwr16xx mmW demo profiles directory for example usage.
        This config is supported only for xWR16xx.
      """
      Command = "bpmCfg"
      Format= "{Command} {subFrameIdx} {enabled} {chirp0Idx} {chirp1Idx}"
      def __init__(self):
        # <subFrameIdx>
        #   subframe Index (exists only in xwr16xx mmW demo)
        self.subFrameIdx = None
        # <enabled>
        #   0 - Disabled
        #   1 - Enabled
        self.enabled = None
        # <chirp0Idx>
        #   BPM enabled:
        #     If BPM is enabled in previous argument, this is the chirp index for the first BPM chirp.
        #     It will have phase 0 on both TX antennas (TX0+ , TX1+).
        #     Note that the chirpCfg command for this chirp index must have both TX antennas enabled.
        #   BPM disabled:
        #     If BPM is disabled, a BPM disable command (set phase to zero on both TX antennas) will be issued for the chirps in the range [chirp 0Idx..chirp1Idx]
        self.chirp0Idx = None
        # <chirp1Idx>
        #   BPM enabled:
        #     If BPM is enabled, this is the chirp index for the second BPM chirp.
        #     It will have phase 0 on TX0 and phase 180 on TX1 (TX0+ , TX1-). 
        #     Note that the chirpCfg command for this chirp index must have both TX antennas enabled.
        #   BPM disabled:
        #     If BPM is disabled, a BPM disable command (set phase to zero on both TX antennas) will be issued for the chirps in the range [chirp 0Idx..chirp1Idx].
        self.chirp1Idx = None
      def parse(self, commandLine: str):
        parts: list[str] = commandLine.split(' ')
        if parts[0] == Configuration_2_1_0.Command.BpmCfg.Command: 
          _ = parts.pop(0)
          if len(parts) == 4:
            self.subFrameIdx = int(parts.pop(0))
          if len(parts) == 3:
            self.enabled = int(parts.pop(0))
            self.chirp0Idx = int(parts.pop(0))
            self.chirp1Idx = int(parts.pop(0))
      @property
      def commandLine(self):
        return Configuration_2_1_0.Command.BpmCfg.Format.format(
          Command = Configuration_2_1_0.Command.BpmCfg.Command, 
          subFrameIdx = str(self.subFrameIdx) if self.subFrameIdx != None else "", 
          enabled = str(self.enabled) if self.enabled != None else "", 
          chirp0Idx = str(self.chirp0Idx) if self.chirp0Idx != None else "", 
          chirp1Idx = str(self.chirp1Idx) if self.chirp1Idx != None else ""
        )
    class LowPower:
      """
        Low Power mode config message to RadarSS.
        See mmwavelink doxgen for details.
        The values in this command should not change between sensorStop and sensorStart.
        Reboot the board to try config with different set of values in this command.
        This is a mandatory command.
      """
      Command = "lowPower"
      Format= "{Command} {dontCare} {adcMode}"
      def __init__(self):
        # <don’t_care>
        self.dontCare = None
        # ADC Mode
        #   0x00 : Regular ADC mode
        #   0x01 : Low power ADC mode
        self.adcMode = None
      def parse(self, commandLine: str):
        parts: list[str] = commandLine.split(' ')
        if parts[0] == Configuration_2_1_0.Command.BpmCfg.Command: 
          _ = parts.pop(0)
          if len(parts) == 2:
            self.dontCare = int(parts.pop(0))
            self.adcMode = int(parts.pop(0))
      @property
      def commandLine(self):
        return Configuration_2_1_0.Command.BpmCfg.Format.format(
          Command = Configuration_2_1_0.Command.BpmCfg.Command, 
          dontCare = str(self.dontCare) if self.dontCare != None else "", 
          adcMode = str(self.adcMode) if self.adcMode != None else ""
        )
    class FrameCfg:
      """
        frame config message to RadarSS and datapath.
        See mmwavelink doxgen for details.
        dfeOutputMode should be set to 1 to use this command.
        The values in this command can be changed between sensorStop and sensorStart.
        This is a mandatory command when dfeOutputMode is set to 1.
      """
      Command = "frameCfg"
      Format= "{Command} {chirpStartIndex} {chirpEndIndex} {numberOfLoops} {numberOfFrames} {framePeriodicity} {triggerSelect} {frameTriggerDelay}"
      def __init__(self):
        # chirp start index (0-511)
        self.chirpStartIndex = None
        # chirp end index (chirp start index-511)
        self.chirpEndIndex = None
        # number of loops (1 to 255)
        self.numberOfLoops = None
        # number of frames (valid range is 0 to 65535, 0 means infinite)
        self.numberOfFrames = None
        # frame periodicity in ms (float values allowed)
        self.framePeriodicity = None
        # trigger select
        #   1: Software trigger.
        #   2: Hardware trigger.
        self.triggerSelect = None
        # Frame trigger delay in ms (float values allowed)
        self.frameTriggerDelay = None
      def parse(self, commandLine: str):
        parts: list[str] = commandLine.split(' ')
        if parts[0] == Configuration_2_1_0.Command.FrameCfg.Command: 
          _ = parts.pop(0)
          if len(parts) == 7:
            self.chirpStartIndex = int(parts.pop(0))
            self.chirpEndIndex = int(parts.pop(0))
            self.numberOfLoops = int(parts.pop(0))
            self.numberOfFrames = int(parts.pop(0))
            self.framePeriodicity = float(parts.pop(0))
            self.triggerSelect = int(parts.pop(0))
            self.frameTriggerDelay = float(parts.pop(0))
      @property
      def commandLine(self):
        return Configuration_2_1_0.Command.FrameCfg.Format.format(
          Command = Configuration_2_1_0.Command.FrameCfg.Command, 
          chirpStartIndex = str(self.chirpStartIndex) if self.chirpStartIndex != None else "", 
          chirpEndIndex = str(self.chirpEndIndex) if self.chirpEndIndex != None else "", 
          numberOfLoops = str(self.numberOfLoops) if self.numberOfLoops != None else "", 
          numberOfFrames = str(self.numberOfFrames) if self.numberOfFrames != None else "", 
          framePeriodicity = str(self.framePeriodicity) if self.framePeriodicity != None else "", 
          triggerSelect = str(self.triggerSelect) if self.triggerSelect != None else "", 
          frameTriggerDelay = str(self.frameTriggerDelay) if self.frameTriggerDelay != None else ""
        )
    class AdvFrameCfg:
      """
        Advanced config message to RadarSS and datapath. 
        See mmwavelink doxgen for details.
        The dfeOutputMode should be set to 3 to use this command. 
        See profile_advanced_subframe.cfg profile in the xwr16xx mmW demo profiles directory for example usage.
        The values in this command can be changed between sensorStop and sensorStart.
        This is a mandatory command when dfeOutputMode is set to 3.
      """
      Command = "advFrameCfg"
      Format= "{Command} {numOfSubFrames} {forceProfile} {numFrames} {triggerSelect} {frameTrigDelay}"
      def __init__(self):
        # <numOfSubFrames>
        #   Number of sub frames enabled in this frame.
        self.numOfSubFrames = None
        # <forceProfile>
        #   Force profile
        self.forceProfile = None
        # <numFrames>
        #   Number of frames to transmit (1 frame: all enabled sub frames)
        self.numFrames = None
        # <triggerSelect>
        #   trigger select
        #     1: Software trigger.
        #     2: Hardware trigger.
        self.triggerSelect = None
        # <frameTrigDelay>
        #   Frame trigger delay in ms (float values allowed)
        self.frameTrigDelay = None
      def parse(self, commandLine: str):
        parts: list[str] = commandLine.split(' ')
        if parts[0] == Configuration_2_1_0.Command.FrameCfg.Command: 
          _ = parts.pop(0)
          if len(parts) == 5:
            self.numOfSubFrames = int(parts.pop(0))
            self.forceProfile = int(parts.pop(0))
            self.numFrames = int(parts.pop(0))
            self.triggerSelect = int(parts.pop(0))
            self.frameTrigDelay = float(parts.pop(0))
      @property
      def commandLine(self):
        return Configuration_2_1_0.Command.FrameCfg.Format.format(
          Command = Configuration_2_1_0.Command.FrameCfg.Command, 
          numOfSubFrames = str(self.numOfSubFrames) if self.numOfSubFrames != None else "", 
          forceProfile = str(self.forceProfile) if self.forceProfile != None else "", 
          numFrames = str(self.numFrames) if self.numFrames != None else "", 
          triggerSelect = str(self.triggerSelect) if self.triggerSelect != None else "", 
          frameTrigDelay = str(self.frameTrigDelay) if self.frameTrigDelay != None else ""
        )
    class SubFrameCfg:
      """
        Subframe config message to RadarSS and datapath. 
        See mmwavelink doxgen for details.
        The dfeOutputMode should be set to 3 to use this command. 
        See profile_advanced_subframe.cfg profile in the xwr16xx mmW demo profiles directory for example usage The values in this command can be changed between sensorStop and sensorStart.
        This is a mandatory command when dfeOutputMode is set to 3.
      """
      Command = "subFrameCfg"
      Format= "{Command} {subFrameNum} {forceProfileIdx} {chirpStartIdx} {numOfChirps} {numLoops} {burstPeriodicity} {chirpStartIdxOffset} {numOfBurst} {numOfBurstLoops} {subFramePeriodicity}"
      def __init__(self):
        # <subFrameNum>
        #   subframe Number for which this command is being given
        self.subFrameNum = None
        # <forceProfileIdx>
        #   Force profile index
        self.forceProfileIdx = None
        # <chirpStartIdx>
        #   Start Index of Chirp
        self.chirpStartIdx = None
        # <numOfChirps>
        #   Num of unique Chirps per burst including start index
        self.numOfChirps = None
        # <numLoops>
        #   No. of times to loop through the unique chirps
        self.numLoops = None
        # <burstPeriodicity>
        #   Burst periodicty in msec (float values allowed) and meets the criteria
        #   burstPeriodicity >= (numLoops)* (numOfChirps) + InterBurstBlankTime
        self.burstPeriodicity = None
        # <chirpStartIdxOffset>
        #   Chirp Start address increament for next burst
        self.chirpStartIdxOffset = None
        # <numOfBurst>
        #   Num of bursts in the subframe
        self.numOfBurst = None
        # <numOfBurstLoops>
        #   Number of times to loop over the set of above defined bursts, in the sub frame
        self.numOfBurstLoops = None
        # <subFramePeriodicity>
        #   subFrame periodicty in msec (float values allowed) and meets the criteria
        #   subFramePeriodicity >= Sum total time of all bursts + InterSubFrameBlankTime
        self.subFramePeriodicity = None
      def parse(self, commandLine: str):
        parts: list[str] = commandLine.split(' ')
        if parts[0] == Configuration_2_1_0.Command.SubFrameCfg.Command: 
          _ = parts.pop(0)
          if len(parts) == 10:
            self.subFrameNum = int(parts.pop(0))
            self.forceProfileIdx = int(parts.pop(0))
            self.chirpStartIdx = int(parts.pop(0))
            self.numOfChirps = int(parts.pop(0))
            self.numLoops = int(parts.pop(0))
            self.burstPeriodicity = float(parts.pop(0))
            self.chirpStartIdxOffset = int(parts.pop(0))
            self.numOfBurst = int(parts.pop(0))
            self.numOfBurstLoops = int(parts.pop(0))
            self.subFramePeriodicity = float(parts.pop(0))
      @property
      def commandLine(self):
        return Configuration_2_1_0.Command.SubFrameCfg.Format.format(
          Command = Configuration_2_1_0.Command.SubFrameCfg.Command, 
          subFrameNum = str(self.subFrameNum) if self.subFrameNum != None else "", 
          forceProfileIdx = str(self.forceProfileIdx) if self.forceProfileIdx != None else "", 
          chirpStartIdx = str(self.chirpStartIdx) if self.chirpStartIdx != None else "", 
          numOfChirps = str(self.numOfChirps) if self.numOfChirps != None else "", 
          numLoops = str(self.numLoops) if self.numLoops != None else "", 
          burstPeriodicity = str(self.burstPeriodicity) if self.burstPeriodicity != None else "", 
          chirpStartIdxOffset = str(self.chirpStartIdxOffset) if self.chirpStartIdxOffset != None else "", 
          numOfBurst = str(self.numOfBurst) if self.numOfBurst != None else "", 
          numOfBurstLoops = str(self.numOfBurstLoops) if self.numOfBurstLoops != None else "", 
          subFramePeriodicity = str(self.subFramePeriodicity) if self.subFramePeriodicity != None else ""
        )
    class GuiMonitor:
      """
        Plot config message to datapath.
        The values in this command can be changed between sensorStop and sensorStart.
        This is a mandatory command.
      """
      Command = "guiMonitor"
      Format= "{Command} {subFrameIdx} {detectedObjects} {logMagnitudeRange} {noiseProfile} {rangeAzimuthHeatMap} {rangeDopplerHeatMap} {statsInfo}"
      def __init__(self):
        # <subFrameIdx>
        #   subframe Index (exists only in xwr16xx mmW demo)
        self.subFrameIdx = None
        # <detected objects>
        #   1 - enable export of detected objects
        #   0 - disable
        self.detectedObjects = None
        # <log magnitude range>
        #   1 - enable export of log magnitude range profile at zero Doppler
        #   0 - disable
        self.logMagnitudeRange = None
        # <noise profile>
        #   1 - enable export of log magnitude noise profile
        #   0 - disable
        self.noiseProfile = None
        # <rangeAzimuthHeatMap>
        #   range-azimuth heat map related information
        #     1 - enable export of zero Doppler radar cube matrix, all range bins, all antennas to calculate and display azimuth heat map.
        #     0 - disable (the GUI computes the FFT of this to show heat map)
        self.rangeAzimuthHeatMap = None
        # <rangeDopplerHeatMap>
        #   range-doppler heat map
        #     1 - enable export of the whole detection matrix. Note that the frame period should be adjusted according to UART transfer time.
        #     0 - disable
        self.rangeDopplerHeatMap = None
        # <statsInfo>
        #   statistics (CPU load, margins, etc)
        #     1 - enable export of stats data.
        #     0 - disable
        self.statsInfo = None
      def parse(self, commandLine: str):
        parts: list[str] = commandLine.split(' ')
        if parts[0] == Configuration_2_1_0.Command.GuiMonitor.Command: 
          _ = parts.pop(0)
          if len(parts) == 7:
            self.subFrameIdx = int(parts.pop(0))
          if len(parts) == 6:
            self.detectedObjects = int(parts.pop(0))
            self.logMagnitudeRange = int(parts.pop(0))
            self.noiseProfile = int(parts.pop(0))
            self.rangeAzimuthHeatMap = int(parts.pop(0))
            self.rangeDopplerHeatMap = int(parts.pop(0))
            self.statsInfo = int(parts.pop(0))
      @property
      def commandLine(self):
        return Configuration_2_1_0.Command.GuiMonitor.Format.format(
          Command = Configuration_2_1_0.Command.GuiMonitor.Command, 
          subFrameIdx = str(self.subFrameIdx) if self.subFrameIdx != None else "", 
          detectedObjects = str(self.detectedObjects) if self.detectedObjects != None else "", 
          logMagnitudeRange = str(self.logMagnitudeRange) if self.logMagnitudeRange != None else "", 
          noiseProfile = str(self.noiseProfile) if self.noiseProfile != None else "", 
          rangeAzimuthHeatMap = str(self.rangeAzimuthHeatMap) if self.rangeAzimuthHeatMap != None else "", 
          rangeDopplerHeatMap = str(self.rangeDopplerHeatMap) if self.rangeDopplerHeatMap != None else "", 
          statsInfo = str(self.statsInfo) if self.statsInfo != None else ""
        )
    class CfarCfg:
      """
        CFAR config message to datapath.
        The values in this command can be changed between sensorStop and sensorStart and even when the sensor is running.
        This is a mandatory command.
      """
      Command = "cfarCfg"
      Format= "{Command} {subFrameIdx} {procDirection} {mode} {noiseWin} {guardLen} {divShift} {cyclicModeOrWrappedAroundMode} {ThresholdScale}"
      def __init__(self):
        # <subFrameIdx>
        #   subframe Index (exists only in xwr16xx mmW demo)
        self.subFrameIdx = None
        # <procDirection>
        #   Processing direction:
        #   0 - CFAR detection in range direction
        #   1 - CFAR detection in Doppler direction
        self.procDirection = None
        # <mode>
        #   CFAR averaging mode:
        #   0 - CFAR_CA (Cell Averaging)
        #   1 - CFAR_CAGO (Cell Averaging Greatest Of)
        #   2 - CFAR_CASO (Cell Averaging Smallest Of)
        self.mode = None
        # <noiseWin>
        #   noise averaging window length:
        #   Length of the noise averaged cells in samples
        self.noiseWin = None
        # <guardLen>
        #   guard length in samples
        self.guardLen = None
        # <divShift>
        #   Cumulative noise sum divisor expressed as a shift.
        #   Sum of noise samples is divided by 2^<divShift>.
        #   Based on platform, <mode> and <noiseWin> , this value should be set as shown in next columns.
        #   The value to be used here should match the "CFAR averaging mode" and the "noise averaging window length" that is selected above.
        #   The actual value that is used for division (2^x) is a power of 2, even though the "noise averaging window length" samples may not have that restriction.
        self.divShift = None
        # cyclic mode or Wrapped around mode.
        #   0- Disabled
        #   1- Enabled
        self.cyclicModeOrWrappedAroundMode = None
        # Threshold scale.
        #   This is used in conjuntion with the noise sum divisor (say x).
        #   the CUT comparison for log input is:
        #   CUT > Threshold scale + (noise sum / 2^x)
        self.ThresholdScale = None
      def parse(self, commandLine: str):
        parts: list[str] = commandLine.split(' ')
        if parts[0] == Configuration_2_1_0.Command.CfarCfg.Command: 
          _ = parts.pop(0)
          if len(parts) == 8:
            self.subFrameIdx = int(parts.pop(0))
          if len(parts) == 7:
            self.procDirection = int(parts.pop(0))
            self.mode = int(parts.pop(0))
            self.noiseWin = int(parts.pop(0))
            self.guardLen = int(parts.pop(0))
            self.divShift = int(parts.pop(0))
            self.cyclicModeOrWrappedAroundMode = int(parts.pop(0))
            self.ThresholdScale = int(parts.pop(0))
      @property
      def commandLine(self):
        return Configuration_2_1_0.Command.CfarCfg.Format.format(
          Command = Configuration_2_1_0.Command.CfarCfg.Command, 
          subFrameIdx = str(self.subFrameIdx) if self.subFrameIdx != None else "", 
          procDirection = str(self.procDirection) if self.procDirection != None else "", 
          mode = str(self.mode) if self.mode != None else "", 
          noiseWin = str(self.noiseWin) if self.noiseWin != None else "", 
          guardLen = str(self.guardLen) if self.guardLen != None else "", 
          divShift = str(self.divShift) if self.divShift != None else "", 
          cyclicModeOrWrappedAroundMode = str(self.cyclicModeOrWrappedAroundMode) if self.cyclicModeOrWrappedAroundMode != None else "", 
          ThresholdScale = str(self.ThresholdScale) if self.ThresholdScale != None else ""
        )
    class PeakGrouping:
      """
        Peak grouping config message to datapath.
        With peak grouping scheme enabled, instead of reporting a cluster of detected neighboring points, only one point, the highest one, will be reported, this reducing the total number of detected points per frame. 
        Only the points between start and end range index are considered. 
        Detected points falling outside this range are dropped and not shipped out as part of point cloud.
        The values in this command can be changed between sensorStop and sensorStart and even when the sensor is running.
        This is a mandatory command.
      """
      Command = "peakGrouping"
      Format= "{Command} {subFrameIdx} {scheme} {peakGroupingInRangeDirection} {peakGroupingInDopplerDirection} {startRangeIndex} {endRangeIndex}"
      def __init__(self):
        # <subFrameIdx>
        #   subframe Index (exists only in xwr16xx mmW demo)
        self.subFrameIdx = None
        # <scheme>
        #   1 - MMW_PEAK_GROUPING_DET_MATRIX_BASED Peak grouping is based on peaks of the neighboring bins read from detection matrix. 
        #       CFAR detected peak is reported if it is greater than its neighbors, located in detection matrix.
        #   2 - MMW_PEAK_GROUPING_CFAR_PEAK_BASED Peak grouping is based on peaks of neighboring bins that are CFAR detected. 
        #       CFAR detected peak is reported if it is greater than its neighbors, located in the list of CFAR detected peaks.
        #   For more detailed look at mmw demo's doxygen documentation.
        self.scheme = None
        # peak grouping in Range direction:
        #   0 - disabled
        #   1 - enabled
        self.peakGroupingInRangeDirection = None
        # peak grouping in Doppler direction:
        #   0 - disabled
        #   1 - enabled
        self.peakGroupingInDopplerDirection = None
        # Start Range Index 
        #   Minimum range index of detected object that should be sent out.
        #   Ex: Value of 1 means Skip 0th bin and start peak grouping from range bin#1
        self.startRangeIndex = None
        # End Range Index 
        #   Maximum range index of detected object that should be sent out.
        #   Ex: Value of (Range FFT size -1) means skip last bin and stop peak grouping at (Range FFT size -1)
        self.endRangeIndex = None
      def parse(self, commandLine: str):
        parts: list[str] = commandLine.split(' ')
        if parts[0] == Configuration_2_1_0.Command.PeakGrouping.Command: 
          _ = parts.pop(0)
          if len(parts) == 6:
            self.subFrameIdx = int(parts.pop(0))
          if len(parts) == 5:
            self.scheme = int(parts.pop(0))
            self.peakGroupingInRangeDirection = int(parts.pop(0))
            self.peakGroupingInDopplerDirection = int(parts.pop(0))
            self.startRangeIndex = int(parts.pop(0))
            self.endRangeIndex = int(parts.pop(0))
      @property
      def commandLine(self):
        return Configuration_2_1_0.Command.PeakGrouping.Format.format(
          Command = Configuration_2_1_0.Command.PeakGrouping.Command, 
          subFrameIdx = str(self.subFrameIdx) if self.subFrameIdx != None else "", 
          scheme = str(self.scheme) if self.scheme != None else "", 
          peakGroupingInRangeDirection = str(self.peakGroupingInRangeDirection) if self.peakGroupingInRangeDirection != None else "", 
          peakGroupingInDopplerDirection = str(self.peakGroupingInDopplerDirection) if self.peakGroupingInDopplerDirection != None else "", 
          startRangeIndex = str(self.startRangeIndex) if self.startRangeIndex != None else "", 
          endRangeIndex = str(self.endRangeIndex) if self.endRangeIndex != None else ""
        )
    class MultiObjBeamForming:
      """
        Multi Object Beamforming config message to datapath.
        This feature allows radar to separate reflections from multiple objects originating from the same range/Doppler detection.
        The procedure searches for the second peak after locating the highest peak in Azimuth FFT.
        If the second peak is greater than the specified threshold, the second object with the same range/Doppler is appended to the list of detected objects.
        The threshold is proportional to the height of the highest peak.
        The values in this command can be changed between sensorStop and sensorStart and even when the sensor is running.
        This is a mandatory command.
      """
      Command = "multiObjBeamForming"
      Format= "{Command} {subFrameIdx} {featureEnabled} {threshold}"
      def __init__(self):
        # <subFrameIdx>
        #   subframe Index (exists only in xwr16xx mmW demo)
        self.subFrameIdx = None
        # <Feature Enabled>
        #   0 - disabled
        #   1 - enabled
        self.featureEnabled = None
        # <threshold>
        #   0 to 1 – threshold scale for the second peak detection in azimuth FFT output.
        #   Detection threshold is equal to <thresholdScale> multiplied by the first peak height.
        #   Note that FFT output is magnitude squared.
        self.threshold = None
      def parse(self, commandLine: str):
        parts: list[str] = commandLine.split(' ')
        if parts[0] == Configuration_2_1_0.Command.MultiObjBeamForming.Command: 
          _ = parts.pop(0)
          if len(parts) == 3:
            self.subFrameIdx = int(parts.pop(0))
          if len(parts) == 2:
            self.featureEnabled = int(parts.pop(0))
            self.threshold = float(parts.pop(0))
      @property
      def commandLine(self):
        return Configuration_2_1_0.Command.MultiObjBeamForming.Format.format(
          Command = Configuration_2_1_0.Command.MultiObjBeamForming.Command, 
          subFrameIdx = str(self.subFrameIdx) if self.subFrameIdx != None else "", 
          featureEnabled = str(self.featureEnabled) if self.featureEnabled != None else "", 
          threshold = str(self.threshold) if self.threshold != None else ""
        )
    class CalibDcRangeSig:
      """
        DC range calibration config message to datapath.
        Antenna coupling signature dominates the range bins close to the radar.
        These are the bins in the range FFT output located around DC.
        When this feature is enabled, the signature is estimated during the first N chirps, and then it is subtracted during the subsequent chirps.
        During the estimation period the specified bins (defined as [negativeBinIdx, positiveBinIdx]) around DC are accumulated and averaged.
        It is assumed that no objects are present in the vicinity of the radar at that time.
        This procedure is initiated by the following CLI command, and it can be initiated any time while radar is running.
        Note that the maximum number of compensated bins is 32.
        The values in this command can be changed between sensorStop and sensorStart and even when the sensor is running.
        This is a mandatory command.
      """
      Command = "calibDcRangeSig"
      Format= "{Command} {subFrameIdx} {enabled} {negativeBinIdx} {positiveBinIdx} {numAvg}"
      def __init__(self):
        # <subFrameIdx>
        #   subframe Index (exists only in xwr16xx mmW demo)
        self.subFrameIdx = None
        # <enabled>
        #   Enable DC removal using first few chirps
        #     0 - disabled
        #     1 - enabled
        self.enabled = None
        # <negativeBinIdx>
        #   negative Bin Index (to remove DC from farthest range bins)
        #   Maximum negative range FFT index to be included for compensation.
        #   Negative indices are indices wrapped around from far end of 1D FFT.
        #   Ex: Value of -5 means last 5 bins starting from the farthest bin
        self.negativeBinIdx = None
        # <positiveBinIdx>
        #   positive Bin Index (to remove DC from closest range bins)
        #   Maximum positive range FFT index to be included for compensation
        #   Value of 8 means first 9 bins (including bin#0)
        self.positiveBinIdx = None
        # <numAvg>
        #   number of chirps to average to collect DC signature (which will then be applied to all chirps beyond this).
        #   The value must be power of 2, and also in xWR14xx, it must be greater than the number of Doppler bins.
        #   Value of 256 means first 256 chirps (after command is issued and feature is enabled) will be used for collecting (averaging) DC signature in the bins specified above.
        #   From 257th chirp, the collected DC signature will be removed from every chirp.
        self.numAvg = None
      def parse(self, commandLine: str):
        parts: list[str] = commandLine.split(' ')
        if parts[0] == Configuration_2_1_0.Command.CalibDcRangeSig.Command: 
          _ = parts.pop(0)
          if len(parts) == 5:
            self.subFrameIdx = int(parts.pop(0))
          if len(parts) == 4:
            self.enabled = int(parts.pop(0))
            self.negativeBinIdx = int(parts.pop(0))
            self.positiveBinIdx = int(parts.pop(0))
            self.numAvg = int(parts.pop(0))
      @property
      def commandLine(self):
        return Configuration_2_1_0.Command.CalibDcRangeSig.Format.format(
          Command = Configuration_2_1_0.Command.CalibDcRangeSig.Command, 
          subFrameIdx = str(self.subFrameIdx) if self.subFrameIdx != None else "", 
          enabled = str(self.enabled) if self.enabled != None else "", 
          negativeBinIdx = str(self.negativeBinIdx) if self.negativeBinIdx != None else "", 
          positiveBinIdx = str(self.positiveBinIdx) if self.positiveBinIdx != None else "", 
          numAvg = str(self.numAvg) if self.numAvg != None else ""
        )
    class ExtendedMaxVelocity:
      """
        Velocity disambiguation config message to datapath.
        A simple technique for velocity disambiguation is implemented.
        It corrects target velocities up to (2*vmax).
        Enabling this feature results in loss of multiObjBeamForming feature.
        See mmW demo doxygen for xwr16xx for more details.
        The values in this command can be changed between sensorStop and sensorStart and even when the sensor is running.
        This is a mandatory command.
      """
      Command = "extendedMaxVelocity"
      Format= "{Command} {subFrameIdx} {enabled}"
      def __init__(self):
        # <subFrameIdx>
        #   subframe Index (exists only in xwr16xx mmW demo)
        self.subFrameIdx = None
        # <enabled>
        #   Enable velocity disambiguation technique
        #     0 - disabled
        #     1 - enabled
        self.enabled = None
      def parse(self, commandLine: str):
        parts: list[str] = commandLine.split(' ')
        if parts[0] == Configuration_2_1_0.Command.ExtendedMaxVelocity.Command: 
          _ = parts.pop(0)
          if len(parts) == 2:
            self.subFrameIdx = int(parts.pop(0))
          if len(parts) == 1:
            self.enabled = int(parts.pop(0))
      @property
      def commandLine(self):
        return Configuration_2_1_0.Command.ExtendedMaxVelocity.Format.format(
          Command = Configuration_2_1_0.Command.ExtendedMaxVelocity.Command, 
          subFrameIdx = str(self.subFrameIdx) if self.subFrameIdx != None else "", 
          enabled = str(self.enabled) if self.enabled != None else ""
        )
    class ClutterRemoval:
      """
        Static clutter removal config message to datapath.
        Static clutter removal algorithm implemented by subtracting from the samples the mean value of the input samples to the 2D-FFT.
        The values in this command can be changed between sensorStop and sensorStart and even when the sensor is running.
        This is a mandatory command.
      """
      Command = "clutterRemoval"
      Format= "{Command} {enabled}"
      def __init__(self):
        # <enabled>
        #   Enable static clutter removal technique
        #     0 - disabled
        #     1 - enabled
        self.enabled = None
      def parse(self, commandLine: str):
        parts: list[str] = commandLine.split(' ')
        if parts[0] == Configuration_2_1_0.Command.ClutterRemoval.Command: 
          _ = parts.pop(0)
          if len(parts) == 1:
            self.enabled = int(parts.pop(0))
      @property
      def commandLine(self):
        return Configuration_2_1_0.Command.ClutterRemoval.Format.format(
          Command = Configuration_2_1_0.Command.ClutterRemoval.Command, 
          enabled = str(self.enabled) if self.enabled != None else ""
        )
    class CompRangeBiasAndRxChanPhase:
      """
        Command for datapath to compensate for bias in the range estimation and receive channel gain and phase imperfections.
        Refer to the procedure mentioned here The values in this command can be changed between sensorStop and sensorStart and even when the sensor is running.
        This is a mandatory command.
      """
      Command = "compRangeBiasAndRxChanPhase"
      Format= "{Command} {rangeBias} {setOfComplexValue}"
      def __init__(self):
        # <rangeBias>
        #   Compensation for range estimation bias in meters supported supported
        self.rangeBias = None
        # <Re(0,0)> <Im(0,0)> <Re(0,1)> <Im(0,1)> ... <Re(0,R-1)> <Im(0,R-1)> <Re(1,0)> <Im(1,0)> ... <Re(T-1,R-1)> <Im(T-1,R-1)>
        #   Set of Complex value representing compensation for virtual Rx channel phase bias in Q15 format.
        #   Pairs of I and Q should be provided for all Tx and Rx antennas in the device
        self.setOfComplexValue = None
      def parse(self, commandLine: str):
        parts: list[str] = commandLine.split(' ')
        if parts[0] == Configuration_2_1_0.Command.CompRangeBiasAndRxChanPhase.Command: 
          _ = parts.pop(0)
          if len(parts) > 1:
            self.rangeBias = float(parts.pop(0))
            self.setOfComplexValue = [int(value) for value in parts] # length == config.numVirtualAntennas
      @property
      def commandLine(self):
        return Configuration_2_1_0.Command.CompRangeBiasAndRxChanPhase.Format.format(
          Command = Configuration_2_1_0.Command.CompRangeBiasAndRxChanPhase.Command, 
          rangeBias = str(self.rangeBias) if self.rangeBias != None else "", 
          setOfComplexValue = ' '.join(map(str, self.setOfComplexValue)) if self.setOfComplexValue != None else ""
        )
    class MeasureRangeBiasAndRxChanPhase:
      """
        Command for datapath to enable the measurement of the range bias and receive channel gain and phase imperfections. 
        Refer to the procedure mentioned here The values in this command can be changed between sensorStop and sensorStart and even when the sensor is running.
        This is a mandatory command.
      """
      Command = "measureRangeBiasAndRxChanPhase"
      Format= "{Command} {enabled} {targetDistance} {searchWin}"
      def __init__(self):
        # <enabled>
        #   1 - enable measurement.
        #       This parameter should be enabled only using the profile_calibration.cfg profile in the mmW demo profiles directory
        #   0 - disable measurement.
        #       This should be the value to use for all other profiles.
        self.enabled = None
        # <targetDistance>
        #   distance in meters where strong reflector is located to be used as test object for measurement. 
        #   This field is only used when measurement mode is enabled.
        self.targetDistance = None
        # <searchWin>
        #   distance in meters of the search window around <targetDistance> where the peak will be searched
        self.searchWin = None
      def parse(self, commandLine: str):
        parts: list[str] = commandLine.split(' ')
        if parts[0] == Configuration_2_1_0.Command.MeasureRangeBiasAndRxChanPhase.Command: 
          _ = parts.pop(0)
          if len(parts) == 3:
            self.enabled = int(parts.pop(0))
            self.targetDistance = float(parts.pop(0))
            self.searchWin = float(parts.pop(0))
      @property
      def commandLine(self):
        return Configuration_2_1_0.Command.MeasureRangeBiasAndRxChanPhase.Format.format(
          Command = Configuration_2_1_0.Command.MeasureRangeBiasAndRxChanPhase.Command, 
          enabled = str(self.enabled) if self.enabled != None else "", 
          targetDistance = str(self.targetDistance) if self.targetDistance != None else "", 
          searchWin = str(self.searchWin) if self.searchWin != None else ""
        )
    class NearFieldCfg:
      """
        OOB processing chain assumes that the object of interests are located in the far field so that the rays between the object and the multiple TX/RX antennas are parallel. 
        However for very close by objects this assumption (of parallel lines) is not valid and can induce a significant phase error when processed using regular FFT techniques.
        User can use this command to enable the near field correction algorithm.
        See mmW demo doxygen for xwr16xx for more details.
      """
      Command = "nearFieldCfg"
      Format= "{Command} {subFrameIdx} {enabled} {startRangeIndex} {endRangeIndex}"
      def __init__(self):
        # <subFrameIdx>
        #   subframe Index (exists only in xwr16xx mmW demo)
        self.subFrameIdx = None
        # <enabled>
        #   Enable near field correction
        #     0 - disabled
        #     1 - enabled
        self.enabled = None
        # <startRangeIndex>
        #   This is the first range bin index at which the algorithm would start correcting
        self.startRangeIndex = None
        # <endRangeIndex>
        #   This is the last range bin index beyond which the algorithm would stop correcting.
        self.endRangeIndex = None
      def parse(self, commandLine: str):
        parts: list[str] = commandLine.split(' ')
        if parts[0] == Configuration_2_1_0.Command.NearFieldCfg.Command: 
          _ = parts.pop(0)
          if len(parts) == 4:
            self.subFrameIdx = int(parts.pop(0))
          if len(parts) == 3:
            self.enabled = int(parts.pop(0))
            self.startRangeIndex = int(parts.pop(0))
            self.endRangeIndex = int(parts.pop(0))
      @property
      def commandLine(self):
        return Configuration_2_1_0.Command.NearFieldCfg.Format.format(
          Command = Configuration_2_1_0.Command.NearFieldCfg.Command, 
          subFrameIdx = str(self.subFrameIdx) if self.subFrameIdx != None else "", 
          enabled = str(self.enabled) if self.enabled != None else "", 
          startRangeIndex = str(self.startRangeIndex) if self.startRangeIndex != None else "", 
          endRangeIndex = str(self.endRangeIndex) if self.endRangeIndex != None else ""
        )
    class CQRxSatMonitor:
      """
        Rx Saturation Monitoring config message for Chirp quality to RadarSS and datapath.
        See mmwavelink doxgen for details on rlRxSatMonConf_t.
      """
      Command = "CQRxSatMonitor"
      Format= "{Command} {profile} {satMonSel} {priSliceDuration} {numSlices} {rxChanMask}"
      def __init__(self):
        # <profile>
        #   Valid profile Id for this monitoring configuraiton.
        #   This profile ID should have a matching profileCfg
        self.profile = None
        # <satMonSel>
        #   RX Saturation monitoring mode
        self.satMonSel = None
        # <priSliceDuration>
        #   Duration of each slice, 1LSB=0.16us, range: 4 - number of ADC samples
        self.priSliceDuration = None
        # <numSlices>
        #   primary + secondary slices , range 1-127.
        #   Maximum primary slice is 64.
        self.numSlices = None
        # <rxChanMask>
        #   RX channgel mask, 1 - Mask, 0 - unmask
        self.rxChanMask = None
      def parse(self, commandLine: str):
        parts: list[str] = commandLine.split(' ')
        if parts[0] == Configuration_2_1_0.Command.CQRxSatMonitor.Command: 
          _ = parts.pop(0)
          if len(parts) == 5:
            self.profile = int(parts.pop(0))
            self.satMonSel = int(parts.pop(0))
            self.priSliceDuration = int(parts.pop(0))
            self.numSlices = int(parts.pop(0))
            self.rxChanMask = int(parts.pop(0))
      @property
      def commandLine(self):
        return Configuration_2_1_0.Command.CQRxSatMonitor.Format.format(
          Command = Configuration_2_1_0.Command.CQRxSatMonitor.Command, 
          profile = str(self.profile) if self.profile != None else "", 
          satMonSel = str(self.satMonSel) if self.satMonSel != None else "", 
          priSliceDuration = str(self.priSliceDuration) if self.priSliceDuration != None else "", 
          numSlices = str(self.numSlices) if self.numSlices != None else "", 
          rxChanMask = str(self.rxChanMask) if self.rxChanMask != None else ""
        )
    class CQSigImgMonitor:
      """
        Signal and image band energy Monitoring config message for Chirp quality to RadarSS and datapath.
        See mmwavelink doxgen for details on rlSigImgMonConf_t.
        The enable/disable for this command is controlled via the "analogMonitor" CLI command
      """
      Command = "CQSigImgMonitor"
      Format= "{Command} {profile} {numSlices} {numSamplePerSlice}"
      def __init__(self):
        # <profile>
        #   Valid profile Id for this monitoring configuraiton.
        #   This profile ID should have a matching profileCfg
        self.profile = None
        # <numSlices>
        #   primary + secondary slices , range 1-127.
        #   Maximum primary slice is 64.
        self.numSlices = None
        # <numSamplePerSlice>
        #   Possible range is 4 to "number of ADC samples" in the corresponding profileCfg.
        #   It must be an even number.
        self.numSamplePerSlice = None
      def parse(self, commandLine: str):
        parts: list[str] = commandLine.split(' ')
        if parts[0] == Configuration_2_1_0.Command.CQSigImgMonitor.Command: 
          _ = parts.pop(0)
          if len(parts) == 3:
            self.profile = int(parts.pop(0))
            self.numSlices = int(parts.pop(0))
            self.numSamplePerSlice = int(parts.pop(0))
      @property
      def commandLine(self):
        return Configuration_2_1_0.Command.CQSigImgMonitor.Format.format(
          Command = Configuration_2_1_0.Command.CQSigImgMonitor.Command, 
          profile = str(self.profile) if self.profile != None else "", 
          numSlices = str(self.numSlices) if self.numSlices != None else "", 
          numSamplePerSlice = str(self.numSamplePerSlice) if self.numSamplePerSlice != None else ""
        )
    class AnalogMonitor:
      """
        Controls the enable/disable of the various monitoring features supported in the demos.
      """
      Command = "analogMonitor"
      Format= "{Command} {rxSaturation} {sigImgBand}"
      def __init__(self):
        # <rxSaturation>
        #   CQRxSatMonitor enable/disable
        #     1:enable
        #     0: disable
        self.rxSaturation = None
        # <sigImgBand>
        #   CQSigImgMonitor enable/disable
        #     1:enable
        #     0: disable
        self.sigImgBand = None
      def parse(self, commandLine: str):
        parts: list[str] = commandLine.split(' ')
        if parts[0] == Configuration_2_1_0.Command.AnalogMonitor.Command: 
          _ = parts.pop(0)
          if len(parts) == 2:
            self.rxSaturation = int(parts.pop(0))
            self.sigImgBand = int(parts.pop(0))
      @property
      def commandLine(self):
        return Configuration_2_1_0.Command.AnalogMonitor.Format.format(
          Command = Configuration_2_1_0.Command.AnalogMonitor.Command, 
          rxSaturation = str(self.rxSaturation) if self.rxSaturation != None else "", 
          sigImgBand = str(self.sigImgBand) if self.sigImgBand != None else "", 
        )
    class LvdsStreamCfg:
      """
        Enables the streaming of various data streams over LVDS lanes (xWR16xx).
      """
      Command = "lvdsStreamCfg"
      Format= "{Command} {subFrameIdx} {enableHeader} {dataFmt} {enableSW}"
      def __init__(self):
        # <subFrameIdx>
        #   subframe Index (exists only in xwr16xx mmW demo)
        self.subFrameIdx = None
        # <enableHeader>
        #   0 - Disable HSI header for all active streams
        #   1 - Enable HSI header for all active streams
        self.enableHeader = None
        # <dataFmt>
        #   Controls HW streaming.
        #   Specifies the HW streaming data format.
        #     0-HW STREAMING DISABLED
        #     1-ADC
        #     2-CP_ADC
        #     3-ADC_CP
        #     4-CP_ADC_CQ
        self.dataFmt = None
        # <enableSW>
        #   0 - Disable user data (SW session)
        #   1 - Enable user data
        self.enableSW = None
      def parse(self, commandLine: str):
        parts: list[str] = commandLine.split(' ')
        if parts[0] == Configuration_2_1_0.Command.LvdsStreamCfg.Command: 
          _ = parts.pop(0)
          if len(parts) == 4:
            self.subFrameIdx = int(parts.pop(0))
          if len(parts) == 3:
            self.enableHeader = int(parts.pop(0))
            self.dataFmt = int(parts.pop(0))
            self.enableSW = int(parts.pop(0))
      @property
      def commandLine(self):
        return Configuration_2_1_0.Command.LvdsStreamCfg.Format.format(
          Command = Configuration_2_1_0.Command.LvdsStreamCfg.Command, 
          subFrameIdx = str(self.subFrameIdx) if self.subFrameIdx != None else "", 
          enableHeader = str(self.enableHeader) if self.enableHeader != None else "", 
          dataFmt = str(self.dataFmt) if self.dataFmt != None else "", 
          enableSW = str(self.enableSW) if self.enableSW != None else "", 
        )
    class SensorStop:
      """
        sensor Stop command to RadarSS and datapath.
        Stops the sensor.
        If the sensor is running, it will stop the mmWave Front End and the processing chain.
        After the command is acknowledged, a new config can be provided and sensor can be restarted or sensor can be restarted without a new config (i.e. using old config).
        See 'sensorStart' command.
        This is mandatory before any reconfiguration is performed post sensorStart.
      """
      Command = "sensorStop"
      Format= "{Command}"
      def __init__(self):
        pass
      def parse(self, commandLine: str):
        parts: list[str] = commandLine.split(' ')
        if parts[0] == Configuration_2_1_0.Command.SensorStop.Command: 
          _ = parts.pop(0)
      @property
      def commandLine(self):
        return Configuration_2_1_0.Command.SensorStop.Format.format(
          Command = Configuration_2_1_0.Command.SensorStop.Command
        )

    def __init__(self):
      self.sensorStart                    = Configuration_2_1_0.Command.SensorStart()
      self.flushCfg                       = Configuration_2_1_0.Command.FlushCfg()
      self.dfeDataOutputMode              = Configuration_2_1_0.Command.DfeDataOutputMode()
      self.channelCfg                     = Configuration_2_1_0.Command.ChannelCfg()
      self.adcCfg                         = Configuration_2_1_0.Command.AdcCfg()
      self.adcbufCfg                      = Configuration_2_1_0.Command.AdcbufCfg()
      self.profileCfg                     = Configuration_2_1_0.Command.ProfileCfg()
      self.bpmCfg                         = Configuration_2_1_0.Command.BpmCfg()
      self.lowPower                       = Configuration_2_1_0.Command.LowPower()
      self.frameCfg                       = Configuration_2_1_0.Command.FrameCfg()
      self.advFrameCfg                    = Configuration_2_1_0.Command.AdvFrameCfg()
      self.subFrameCfg                    = Configuration_2_1_0.Command.SubFrameCfg()
      self.guiMonitor                     = Configuration_2_1_0.Command.GuiMonitor()
      self.cfarCfg                        = Configuration_2_1_0.Command.CfarCfg()
      self.peakGrouping                   = Configuration_2_1_0.Command.PeakGrouping()
      self.multiObjBeamForming            = Configuration_2_1_0.Command.MultiObjBeamForming()
      self.calibDcRangeSig                = Configuration_2_1_0.Command.CalibDcRangeSig()
      self.extendedMaxVelocity            = Configuration_2_1_0.Command.ExtendedMaxVelocity()
      self.clutterRemoval                 = Configuration_2_1_0.Command.ClutterRemoval()
      self.compRangeBiasAndRxChanPhase    = Configuration_2_1_0.Command.CompRangeBiasAndRxChanPhase()
      self.measureRangeBiasAndRxChanPhase = Configuration_2_1_0.Command.MeasureRangeBiasAndRxChanPhase()
      self.nearFieldCfg                   = Configuration_2_1_0.Command.NearFieldCfg()
      self.cQRxSatMonitor                 = Configuration_2_1_0.Command.CQRxSatMonitor()
      self.cQSigImgMonitor                = Configuration_2_1_0.Command.CQSigImgMonitor()
      self.analogMonitor                  = Configuration_2_1_0.Command.AnalogMonitor()
      self.lvdsStreamCfg                  = Configuration_2_1_0.Command.LvdsStreamCfg()
      self.sensorStop                     = Configuration_2_1_0.Command.SensorStop()
      self.chirpCfg_list: list[Configuration_2_1_0.Command.ChirpCfg] = list()
    def parse(self, commandLine: str):
      commandLine = commandLine.strip()
      if commandLine.startswith("sensorStart"): self.sensorStart.parse(commandLine)
      if commandLine.startswith("flushCfg"): self.flushCfg.parse(commandLine)
      if commandLine.startswith("dfeDataOutputMode"): self.dfeDataOutputMode.parse(commandLine)
      if commandLine.startswith("channelCfg"): self.channelCfg.parse(commandLine)
      if commandLine.startswith("adcCfg"): self.adcCfg.parse(commandLine)
      if commandLine.startswith("adcbufCfg"): self.adcbufCfg.parse(commandLine)
      if commandLine.startswith("profileCfg"): self.profileCfg.parse(commandLine)
      if commandLine.startswith("bpmCfg"): self.bpmCfg.parse(commandLine)
      if commandLine.startswith("lowPower"): self.lowPower.parse(commandLine)
      if commandLine.startswith("frameCfg"): self.frameCfg.parse(commandLine)
      if commandLine.startswith("advFrameCfg"): self.advFrameCfg.parse(commandLine)
      if commandLine.startswith("subFrameCfg"): self.subFrameCfg.parse(commandLine)
      if commandLine.startswith("guiMonitor"): self.guiMonitor.parse(commandLine)
      if commandLine.startswith("cfarCfg"): self.cfarCfg.parse(commandLine)
      if commandLine.startswith("peakGrouping"): self.peakGrouping.parse(commandLine)
      if commandLine.startswith("multiObjBeamForming"): self.multiObjBeamForming.parse(commandLine)
      if commandLine.startswith("calibDcRangeSig"): self.calibDcRangeSig.parse(commandLine)
      if commandLine.startswith("extendedMaxVelocity"): self.extendedMaxVelocity.parse(commandLine)
      if commandLine.startswith("clutterRemoval"): self.clutterRemoval.parse(commandLine)
      if commandLine.startswith("compRangeBiasAndRxChanPhase"): self.compRangeBiasAndRxChanPhase.parse(commandLine)
      if commandLine.startswith("measureRangeBiasAndRxChanPhase"): self.measureRangeBiasAndRxChanPhase.parse(commandLine)
      if commandLine.startswith("nearFieldCfg"): self.nearFieldCfg.parse(commandLine)
      if commandLine.startswith("cQRxSatMonitor"): self.cQRxSatMonitor.parse(commandLine)
      if commandLine.startswith("cQSigImgMonitor"): self.cQSigImgMonitor.parse(commandLine)
      if commandLine.startswith("analogMonitor"): self.analogMonitor.parse(commandLine)
      if commandLine.startswith("lvdsStreamCfg"): self.lvdsStreamCfg.parse(commandLine)
      if commandLine.startswith("sensorStop"): self.sensorStop.parse(commandLine)
      if commandLine.startswith("chirpCfg"): 
        txAntennaEnableMask_list = [chirpCfg.txAntennaEnableMask for chirpCfg in self.chirpCfg_list]
        chirpCfg = Configuration_2_1_0.Command.ChirpCfg()
        chirpCfg.parse(commandLine)
        if chirpCfg.txAntennaEnableMask not in txAntennaEnableMask_list:
          # self.chirpCfg_list.append(chirpCfg)
          self.chirpCfg_list.append(Configuration_2_1_0.Command.ChirpCfg())
          self.chirpCfg_list[-1].parse(commandLine)
          pass
        else:
          for i in range(len(txAntennaEnableMask_list)):
            if chirpCfg.txAntennaEnableMask == txAntennaEnableMask_list[i]:
              self.chirpCfg_list[i].parse(commandLine)
        pass
      pass
    def commandLines(self, sensorStop: bool = False, sensorStart: bool = False):
      commandLines: list[str] = []
      if sensorStop: commandLines.append(self.sensorStop.Command)
      commandLines.append(self.flushCfg.Command)
      commandLines.append(self.dfeDataOutputMode.Command)
      commandLines.append(self.channelCfg.Command)
      commandLines.append(self.adcCfg.Command)
      commandLines.append(self.adcbufCfg.Command)
      commandLines.append(self.profileCfg.Command)
      for chirpCfg in self.chirpCfg_list:
        commandLines.append(chirpCfg.Command)
      commandLines.append(self.bpmCfg.Command)
      commandLines.append(self.lowPower.Command)
      commandLines.append(self.frameCfg.Command)
      commandLines.append(self.advFrameCfg.Command)
      commandLines.append(self.subFrameCfg.Command)
      commandLines.append(self.guiMonitor.Command)
      commandLines.append(self.cfarCfg.Command)
      commandLines.append(self.peakGrouping.Command)
      commandLines.append(self.multiObjBeamForming.Command)
      commandLines.append(self.calibDcRangeSig.Command)
      commandLines.append(self.extendedMaxVelocity.Command)
      commandLines.append(self.clutterRemoval.Command)
      commandLines.append(self.compRangeBiasAndRxChanPhase.Command)
      commandLines.append(self.measureRangeBiasAndRxChanPhase.Command)
      commandLines.append(self.nearFieldCfg.Command)
      commandLines.append(self.cQRxSatMonitor.Command)
      commandLines.append(self.cQSigImgMonitor.Command)
      commandLines.append(self.analogMonitor.Command)
      commandLines.append(self.lvdsStreamCfg.Command)
      if sensorStart: commandLines.append(self.sensorStart.Command)
      return commandLines

  # commandParameters_backup = dict()

  class Parameter:
    """
    """
    def __init__(self) -> None:
      self.numRxAnt = None 
      self.numTxAnt = None 
      self.numVirtualAntennas = None 
      self.framePeriodicity = None 
      self.numDopplerBins = None 
      self.numRangeBins = None 
      self.rangeResolutionMeters = None 
      self.rangeIdxToMeters = None 
      self.dopplerResolutionMps = None 
      self.maxRange = None 
      self.maxVelocity = None 
      self.thresholdScaleDb = None 
      self.logger = Log.Logger(fileName="Log/Configuration_2_1_0.log")

    def parse(self, platform, command, verificationLevel: str="Error"): # Todo: trans to use `setter` and `getter`
      command: Configuration_2_1_0.Command = command
      def decode_mask(mask: int) -> int:
        value = 0
        while mask :
          mask >>= 1
          value += 1
        return value

      Missing_Command = False

      if not Missing_Command: 
        try:
          self.numRxAnt = decode_mask(mask=int(command.channelCfg.rxChannelEn))
          self.numTxAnt = decode_mask(mask=int(command.channelCfg.txChannelEn))
          self.numVirtualAntennas = self.numRxAnt * self.numTxAnt
        except TypeError:
          Missing_Command = True
          self.logger.log(event="Configuration_2_1_0.Parameter.parse", level=verificationLevel, message="Missing command: `channelCfg`")

      if not Missing_Command: 
        try:
          startFreq = command.profileCfg.startFreq
          idleTime = command.profileCfg.idleTime
          rampEndTime = command.profileCfg.rampEndTime
          freqSlopeConst = command.profileCfg.freqSlopeConst
          numAdcSamples = command.profileCfg.numAdcSamples
          numAdcSamplesRoundTo2 = 1
          while numAdcSamples > numAdcSamplesRoundTo2: numAdcSamplesRoundTo2 = numAdcSamplesRoundTo2 << 1
          digOutSampleRate = command.profileCfg.digOutSampleRate
        except TypeError:
          Missing_Command = True
          self.logger.log(event="Configuration_2_1_0.Parameter.parse", level=verificationLevel, message="Missing command: `profileCfg`")

      if not Missing_Command: 
        try:
          chirpStartIdx = command.frameCfg.chirpStartIndex
          chirpEndIdx = command.frameCfg.chirpEndIndex
          numLoops = command.frameCfg.numberOfLoops
          numFrames = command.frameCfg.numberOfFrames
          self.framePeriodicity = command.frameCfg.framePeriodicity
          numChirpsPerFrame = (chirpEndIdx - chirpStartIdx + 1) * numLoops
        except TypeError:
          Missing_Command = True
          self.logger.log(event="Configuration_2_1_0.Parameter.parse", level=verificationLevel, message="Missing command: `frameCfg`")

      if not Missing_Command: 
        try:
          if platform == "xWR14xx":
            self.thresholdScaleDb = (command.cfarCfg.ThresholdScale * 6 * 2**math.ceil(math.log2(self.numVirtualAntennas))) // (512 * self.numVirtualAntennas)
          if platform == "xWR16xx":
            self.thresholdScaleDb = (command.cfarCfg.ThresholdScale * 6) // (256 * self.numVirtualAntennas)
        except TypeError:
          Missing_Command = True
          self.logger.log(event="Configuration_2_1_0.Parameter.parse", level=verificationLevel, message="Missing command: `cfarCfg`")

      if not Missing_Command: 
        self.numDopplerBins = numChirpsPerFrame / self.numTxAnt
        self.numRangeBins = numAdcSamplesRoundTo2
        self.rangeResolutionMeters = (3e8 * digOutSampleRate * 1e3) / (2 * freqSlopeConst * 1e12 * numAdcSamples)
        self.rangeIdxToMeters = (3e8 * digOutSampleRate * 1e3) / (2 * freqSlopeConst * 1e12 * self.numRangeBins)
        self.dopplerResolutionMps = 3e8 / (2 * startFreq * 1e9 * (idleTime + rampEndTime) * 1e-6 * self.numDopplerBins * self.numTxAnt)
        self.maxRange = (300 * 0.9 * digOutSampleRate)/(2 * freqSlopeConst * 1e3)
        self.maxVelocity = 3e8 / (4 * startFreq * 1e9 * (idleTime + rampEndTime) * 1e-6 * self.numTxAnt)
        self.logger.log(event="Configuration_2_1_0.Parameter.parse", level="information", message="parse configParameters success")

  def __init__(self, platform: str) -> None:
    self.platform: str = platform
    self.command: Configuration_2_1_0.Command = Configuration_2_1_0.Command()
    self.parameter: Configuration_2_1_0.Parameter = Configuration_2_1_0.Parameter() 
    self.logger = Log.Logger(fileName="Log/Configuration_2_1_0.log")

  def parse_commandLine(self, commandLine: str):
    commandLine = commandLine.strip()
    parts: list[str] = commandLine.split(" ")
    self.command.parse(commandLine)
    if parts[0] == "sensorStart" or parts[0] == "channelCfg" or parts[0] == "profileCfg" or parts[0] == "frameCfg" or parts[0] == "cfarCfg":
      self.parameter.parse(self.platform, self.command)

  def set_CfarRangeThreshold_dB(self, threshold_dB: int|float):
    if threshold_dB<0 or threshold_dB>100: 
      return
    else: 
      self.parameter.thresholdScaleDb = threshold_dB
      if self.platform == "xWR14xx":
        self.command.cfarCfg.ThresholdScale = (threshold_dB * 512 * self.parameter.numVirtualAntennas) // (6 * 2**math.ceil(math.log2(self.parameter.numVirtualAntennas)))
      if self.platform == "xWR16xx":
        self.command.cfarCfg.ThresholdScale = (threshold_dB * 256 * self.parameter.numVirtualAntennas) // 6

  def set_RemoveStaticClutter(self, enabled: bool):
    self.command.clutterRemoval.enabled = int(enabled)

  def set_FramePeriodicity(self, milliseconds: int|float):
    self.command.frameCfg.framePeriodicity = milliseconds
    self.parameter.framePeriodicity = milliseconds

  # command = None
  # config = None

  # def __init__(self, platform: str):
  #   self.command = self.Command()
  #   self.config = self.Config()
  #   self.logger = Log.Logger(fileName="Log/Configuration_2_1_0.log")
  #   if platform == "xWR14xx":
  #     self.platform = platform
  #     del self.command.adcbufCfg.subFrameIdx
  #     del self.command.bpmCfg.subFrameIdx
  #     del self.command.bpmCfg.enabled
  #     del self.command.bpmCfg.chirp0Idx
  #     del self.command.bpmCfg.chirp1Idx
  #     del self.command.bpmCfg
  #     del self.command.advFrameCfg.numOfSubFrames
  #     del self.command.advFrameCfg.forceProfile
  #     del self.command.advFrameCfg.numFrames
  #     del self.command.advFrameCfg.triggerSelect
  #     del self.command.advFrameCfg.frameTrigDelay
  #     del self.command.advFrameCfg
  #     del self.command.subFrameCfg.subFrameNum
  #     del self.command.subFrameCfg.forceProfileIdx
  #     del self.command.subFrameCfg.chirpStartIdx
  #     del self.command.subFrameCfg.numOfChirps
  #     del self.command.subFrameCfg.numLoops
  #     del self.command.subFrameCfg.burstPeriodicity
  #     del self.command.subFrameCfg.chirpStartIdxOffset
  #     del self.command.subFrameCfg.numOfBurst
  #     del self.command.subFrameCfg.numOfBurstLoops
  #     del self.command.subFrameCfg.subFramePeriodicity
  #     del self.command.subFrameCfg
  #     del self.command.guiMonitor.subFrameIdx
  #     del self.command.cfarCfg.subFrameIdx
  #     del self.command.peakGrouping.subFrameIdx
  #     del self.command.multiObjBeamForming.subFrameIdx
  #     del self.command.calibDcRangeSig.subFrameIdx
  #     del self.command.extendedMaxVelocity.subFrameIdx
  #     del self.command.extendedMaxVelocity.enabled
  #     del self.command.extendedMaxVelocity
  #     del self.command.nearFieldCfg.subFrameIdx
  #     del self.command.nearFieldCfg.enabled
  #     del self.command.nearFieldCfg.startRangeIndex
  #     del self.command.nearFieldCfg.endRangeIndex
  #     del self.command.nearFieldCfg
  #     del self.command.lvdsStreamCfg.subFrameIdx
  #     del self.command.lvdsStreamCfg.enableHeader
  #     del self.command.lvdsStreamCfg.dataFmt
  #     del self.command.lvdsStreamCfg.enableSW
  #     del self.command.lvdsStreamCfg
  #   if platform == "xWR16xx":
  #     self.platform = platform
  #   self.commandParameters_backup = copy.deepcopy(self.commandParameters)
# %%
  # def set(self, command: str, parameters: str, value):
  #   self.commandParameters[command][parameters] = value
  # def get(self, command: str, parameters: str):
  #   return self.commandParameters[command][parameters]
  
  # def parse_commandParameters_1443(self, command: str):
  #   try:
  #     units: list[str] = command.split(' ')
  #     if units[0] == "dfeDataOutputMode": 
  #       self.commandParameters["dfeDataOutputMode"]["modeType"] = int(units[1])
  #     if units[0] == "channelCfg": 
  #       self.commandParameters["channelCfg"]["rxChannelEn"] = int(units[1])
  #       self.commandParameters["channelCfg"]["txChannelEn"] = int(units[2])
  #       self.commandParameters["channelCfg"]["cascading"] = int(units[3])
  #       self.parse_configParameters_1443(verificationLevel="Warning")
  #     if units[0] == "adcCfg": 
  #       self.commandParameters["adcCfg"]["numADCBits"] = int(units[1])
  #       self.commandParameters["adcCfg"]["adcOutputFmt"] = int(units[2])
  #     if units[0] == "adcbufCfg": 
  #       # self.commandParameters["adcbufCfg"]["subFrameIdx"] = None
  #       self.commandParameters["adcbufCfg"]["adcOutputFmt"] = int(units[1])
  #       self.commandParameters["adcbufCfg"]["SampleSwap"] = int(units[2])
  #       self.commandParameters["adcbufCfg"]["ChanInterleave"] = int(units[3])
  #       self.commandParameters["adcbufCfg"]["ChirpThreshold"] = int(units[4])
  #     if units[0] == "profileCfg": 
  #       self.commandParameters["profileCfg"]["profileId"] = int(units[1])
  #       self.commandParameters["profileCfg"]["startFreq"] = float(units[2])
  #       self.commandParameters["profileCfg"]["idleTime"] = float(units[3])
  #       self.commandParameters["profileCfg"]["adcStartTime"] = float(units[4])
  #       self.commandParameters["profileCfg"]["rampEndTime"] = float(units[5])
  #       self.commandParameters["profileCfg"]["txOutPower"] = int(units[6])
  #       self.commandParameters["profileCfg"]["txPhaseShifter"] = int(units[7])
  #       self.commandParameters["profileCfg"]["freqSlopeConst"] = float(units[8])
  #       self.commandParameters["profileCfg"]["txStartTime"] = float(units[9])
  #       self.commandParameters["profileCfg"]["numAdcSamples"] = int(units[10])
  #       self.commandParameters["profileCfg"]["digOutSampleRate"] = int(units[11])
  #       self.commandParameters["profileCfg"]["hpfCornerFreq1"] = int(units[12])
  #       self.commandParameters["profileCfg"]["hpfCornerFreq2"] = int(units[13])
  #       self.commandParameters["profileCfg"]["rxGain"] = int(units[14])
  #       self.parse_configParameters_1443(verificationLevel="Warning")
  #     if units[0] == "chirpCfg": 
  #       self.commandParameters["chirpCfg"]["chirpStartIndex"] = int(units[1])
  #       self.commandParameters["chirpCfg"]["chirpEndIndex"] = int(units[2])
  #       self.commandParameters["chirpCfg"]["profileIdentifier"] = float(units[3])
  #       self.commandParameters["chirpCfg"]["startFrequencyVariation"] = int(units[4])
  #       self.commandParameters["chirpCfg"]["frequencySlopeVariation"] = float(units[5])
  #       self.commandParameters["chirpCfg"]["idleTimeVariation"] = float(units[6])
  #       self.commandParameters["chirpCfg"]["adcStartTimeVariation"] = float(units[7])
  #       self.commandParameters["chirpCfg"]["txAntennaEnableMask"] = int(units[8])
  #     # if units[0] == "bpmCfg": 
  #     #   self.commandParameters["bpmCfg"]["subFrameIdx"] = None
  #     #   self.commandParameters["bpmCfg"]["enabled"] = None
  #     #   self.commandParameters["bpmCfg"]["chirp0Idx"] = None
  #     #   self.commandParameters["bpmCfg"]["chirp1Idx"] = None
  #     if units[0] == "lowPower": 
  #       self.commandParameters["lowPower"]["dontCare"] = int(units[1])
  #       self.commandParameters["lowPower"]["adcMode"] = int(units[2])
  #     if units[0] == "frameCfg": 
  #       self.commandParameters["frameCfg"]["chirpStartIndex"] = int(units[1])
  #       self.commandParameters["frameCfg"]["chirpEndIndex"] = int(units[2])
  #       self.commandParameters["frameCfg"]["numberOfLoops"] = int(units[3])
  #       self.commandParameters["frameCfg"]["numberOfFrames"] = int(units[4])
  #       self.commandParameters["frameCfg"]["framePeriodicity"] = float(units[5])
  #       self.commandParameters["frameCfg"]["triggerSelect"] = int(units[6])
  #       self.commandParameters["frameCfg"]["frameTriggerDelay"] = float(units[7])
  #       self.parse_configParameters_1443(verificationLevel="Warning")
  #     if units[0] == "advFrameCfg": 
  #       self.commandParameters["advFrameCfg"]["numOfSubFrames"] = int(units[1])
  #       self.commandParameters["advFrameCfg"]["forceProfile"] = int(units[2])
  #       self.commandParameters["advFrameCfg"]["numFrames"] = int(units[3])
  #       self.commandParameters["advFrameCfg"]["triggerSelect"] = int(units[4])
  #       self.commandParameters["advFrameCfg"]["frameTrigDelay"] = float(units[5])
  #     if units[0] == "subFrameCfg": 
  #       self.commandParameters["subFrameCfg"]["subFrameNum"] = int(units[1])
  #       self.commandParameters["subFrameCfg"]["forceProfileIdx"] = int(units[2])
  #       self.commandParameters["subFrameCfg"]["chirpStartIdx"] = int(units[3])
  #       self.commandParameters["subFrameCfg"]["numOfChirps"] = int(units[4])
  #       self.commandParameters["subFrameCfg"]["numLoops"] = int(units[5])
  #       self.commandParameters["subFrameCfg"]["burstPeriodicity"] = float(units[6])
  #       self.commandParameters["subFrameCfg"]["chirpStartIdxOffset"] = int(units[7])
  #       self.commandParameters["subFrameCfg"]["numOfBurst"] = int(units[8])
  #       self.commandParameters["subFrameCfg"]["numOfBurstLoops"] = int(units[9])
  #       self.commandParameters["subFrameCfg"]["subFramePeriodicity"] = float(units[10])
  #     if units[0] == "guiMonitor": 
  #       # self.commandParameters["guiMonitor"]["subFrameIdx"] = None
  #       self.commandParameters["guiMonitor"]["detectedObjects"] = int(units[1])
  #       self.commandParameters["guiMonitor"]["logMagnitudeRange"] = int(units[2])
  #       self.commandParameters["guiMonitor"]["noiseProfile"] = int(units[3])
  #       self.commandParameters["guiMonitor"]["rangeAzimuthHeatMap"] = int(units[4])
  #       self.commandParameters["guiMonitor"]["rangeDopplerHeatMap"] = int(units[5])
  #       self.commandParameters["guiMonitor"]["statsInfo"] = int(units[6])
  #     if units[0] == "cfarCfg": 
  #       # self.commandParameters["cfarCfg"]["subFrameIdx"] = None
  #       self.commandParameters["cfarCfg"]["procDirection"] = int(units[1])
  #       self.commandParameters["cfarCfg"]["mode"] = int(units[2])
  #       self.commandParameters["cfarCfg"]["noiseWin"] = int(units[3])
  #       self.commandParameters["cfarCfg"]["guardLen"] = int(units[4])
  #       self.commandParameters["cfarCfg"]["divShift"] = int(units[5])
  #       self.commandParameters["cfarCfg"]["cyclicModeOrWrappedAroundMode"] = int(units[6])
  #       self.commandParameters["cfarCfg"]["ThresholdScale"] = int(units[7])
  #       self.parse_configParameters_1443(verificationLevel="Warning")
  #     if units[0] == "peakGrouping": 
  #       # self.commandParameters["peakGrouping"]["subFrameIdx"] = None
  #       self.commandParameters["peakGrouping"]["scheme"] = int(units[1])
  #       self.commandParameters["peakGrouping"]["peakGroupingInRangeDirection"] = int(units[2])
  #       self.commandParameters["peakGrouping"]["peakGroupingInDopplerDirection"] = int(units[3])
  #       self.commandParameters["peakGrouping"]["startRangeIndex"] = int(units[4])
  #       self.commandParameters["peakGrouping"]["endRangeIndex"] = int(units[5])
  #     if units[0] == "multiObjBeamForming": 
  #       # self.commandParameters["multiObjBeamForming"]["subFrameIdx"] = None
  #       self.commandParameters["multiObjBeamForming"]["featureEnabled"] = int(units[1])
  #       self.commandParameters["multiObjBeamForming"]["threshold"] = float(units[2])
  #     if units[0] == "calibDcRangeSig": 
  #       # self.commandParameters["calibDcRangeSig"]["subFrameIdx"] = None
  #       self.commandParameters["calibDcRangeSig"]["enabled"] = int(units[1])
  #       self.commandParameters["calibDcRangeSig"]["negativeBinIdx"] = int(units[2])
  #       self.commandParameters["calibDcRangeSig"]["positiveBinIdx"] = int(units[3])
  #       self.commandParameters["calibDcRangeSig"]["numAvg"] = int(units[4])
  #     if units[0] == "extendedMaxVelocity": 
  #       # self.commandParameters["extendedMaxVelocity"]["subFrameIdx"] = None
  #       self.commandParameters["extendedMaxVelocity"]["enabled"] = int(units[1])
  #     if units[0] == "clutterRemoval": 
  #       self.commandParameters["clutterRemoval"]["enabled"] = int(units[1])
  #     if units[0] == "compRangeBiasAndRxChanPhase": 
  #       self.commandParameters["compRangeBiasAndRxChanPhase"]["rangeBias"] = float(units[1])
  #       self.commandParameters["compRangeBiasAndRxChanPhase"]["setOfComplexValue"] = [int(value) for value in units[2:]] # length == self.configParameters["numVirtualAntennas"]
  #     if units[0] == "measureRangeBiasAndRxChanPhase": 
  #       self.commandParameters["measureRangeBiasAndRxChanPhase"]["enabled"] = int(units[1])
  #       self.commandParameters["measureRangeBiasAndRxChanPhase"]["targetDistance"] = float(units[2])
  #       self.commandParameters["measureRangeBiasAndRxChanPhase"]["searchWin"] = float(units[3])
  #     if units[0] == "nearFieldCfg": 
  #       # self.commandParameters["nearFieldCfg"]["subFrameIdx"] = None
  #       self.commandParameters["nearFieldCfg"]["enabled"] = int(units[1])
  #       self.commandParameters["nearFieldCfg"]["startRangeIndex"] = int(units[2])
  #       self.commandParameters["nearFieldCfg"]["endRangeIndex"] = int(units[3])
  #     if units[0] == "CQRxSatMonitor": 
  #       self.commandParameters["CQRxSatMonitor"]["profile"] = int(units[1])
  #       self.commandParameters["CQRxSatMonitor"]["satMonSel"] = int(units[2])
  #       self.commandParameters["CQRxSatMonitor"]["priSliceDuration"] = int(units[3])
  #       self.commandParameters["CQRxSatMonitor"]["numSlices"] = int(units[4])
  #       self.commandParameters["CQRxSatMonitor"]["rxChanMask"] = int(units[5])
  #     if units[0] == "CQSigImgMonitor": 
  #       self.commandParameters["CQSigImgMonitor"]["profile"] = int(units[1])
  #       self.commandParameters["CQSigImgMonitor"]["numSlices"] = int(units[2])
  #       self.commandParameters["CQSigImgMonitor"]["numSamplePerSlice"] = int(units[3])
  #     if units[0] == "analogMonitor": 
  #       self.commandParameters["analogMonitor"]["rxSaturation"] = int(units[1])
  #       self.commandParameters["analogMonitor"]["sigImgBand"] = int(units[2])
  #     if units[0] == "lvdsStreamCfg": 
  #       # self.commandParameters["lvdsStreamCfg"]["subFrameIdx"] = None
  #       self.commandParameters["lvdsStreamCfg"]["enableHeader"] = int(units[1])
  #       self.commandParameters["lvdsStreamCfg"]["dataFmt"] = int(units[2])
  #       self.commandParameters["lvdsStreamCfg"]["enableSW"] = int(units[3])
  #     if units[0] == "sensorStart": 
  #       if len(units) > 1:
  #         self.commandParameters["sensorStart"]["doReconfig"] = int(units[1])
  #         self.parse_configParameters_1443()
  #     if units[0] == "sensorStop": 
  #       pass
  #     if units[0] == "flushCfg": 
  #       # todo: flush commandParameters
  #       pass
  #   except: 
  #     self.logger.log(event="parse_commandParameters_1443", level="Error", message="Parse error from: `{command}`".format(command=str(command)))

  # def parse_commandParameters(self, commandLine: str):

  #   def allNone(iterator):
  #     for i in iterator:
  #       if i is not None: return False
  #     return True
    
  #   try:
  #     clips: list[str] = commandLine.split(' ')
  #     main: str = clips.pop(0)
  #     if main == "sensorStart": 
  #       if len(clips) > 1:
  #         self.commandParameters["sensorStart"]["doReconfig"] = int(clips.pop(0))
  #         self.parse_configParameters()
  #     if main == "flushCfg": 
  #       self.commandParameters = copy.deepcopy(self.commandParameters_backup)
  #     if main == "dfeDataOutputMode": 
  #       self.commandParameters["dfeDataOutputMode"]["modeType"] = int(clips.pop(0))
  #     if main == "channelCfg": 
  #       self.commandParameters["channelCfg"]["rxChannelEn"] = int(clips.pop(0))
  #       self.commandParameters["channelCfg"]["txChannelEn"] = int(clips.pop(0))
  #       self.commandParameters["channelCfg"]["cascading"] = int(clips.pop(0))
  #       self.parse_configParameters(verificationLevel="Warning")
  #       # clear `chirpCfg`
  #       # self.commandParameters["chirpCfg"] = [self.commandParameters["chirpCfg"][0].copy()]
  #       # for keys in self.commandParameters["chirpCfg"][0].keys():
  #       #   self.commandParameters["chirpCfg"][0][keys] = None
  #     if main == "adcCfg": 
  #       self.commandParameters["adcCfg"]["numADCBits"] = int(clips.pop(0))
  #       self.commandParameters["adcCfg"]["adcOutputFmt"] = int(clips.pop(0))
  #     if main == "adcbufCfg": 
  #       if self.platform == "xwr16xx":
  #         self.commandParameters["adcbufCfg"]["subFrameIdx"] = int(clips.pop(0))
  #       else: pass
  #       self.commandParameters["adcbufCfg"]["adcOutputFmt"] = int(clips.pop(0))
  #       self.commandParameters["adcbufCfg"]["SampleSwap"] = int(clips.pop(0))
  #       self.commandParameters["adcbufCfg"]["ChanInterleave"] = int(clips.pop(0))
  #       self.commandParameters["adcbufCfg"]["ChirpThreshold"] = int(clips.pop(0))
  #     if main == "profileCfg": 
  #       self.commandParameters["profileCfg"]["profileId"] = int(clips.pop(0))
  #       self.commandParameters["profileCfg"]["startFreq"] = float(clips.pop(0))
  #       self.commandParameters["profileCfg"]["idleTime"] = float(clips.pop(0))
  #       self.commandParameters["profileCfg"]["adcStartTime"] = float(clips.pop(0))
  #       self.commandParameters["profileCfg"]["rampEndTime"] = float(clips.pop(0))
  #       self.commandParameters["profileCfg"]["txOutPower"] = int(clips.pop(0))
  #       self.commandParameters["profileCfg"]["txPhaseShifter"] = int(clips.pop(0))
  #       self.commandParameters["profileCfg"]["freqSlopeConst"] = float(clips.pop(0))
  #       self.commandParameters["profileCfg"]["txStartTime"] = float(clips.pop(0))
  #       self.commandParameters["profileCfg"]["numAdcSamples"] = int(clips.pop(0))
  #       self.commandParameters["profileCfg"]["digOutSampleRate"] = int(clips.pop(0))
  #       self.commandParameters["profileCfg"]["hpfCornerFreq1"] = int(clips.pop(0))
  #       self.commandParameters["profileCfg"]["hpfCornerFreq2"] = int(clips.pop(0))
  #       self.commandParameters["profileCfg"]["rxGain"] = int(clips.pop(0))
  #       self.parse_configParameters(verificationLevel="Warning")
  #     if main == "chirpCfg": 
  #       # if length == 1 and all None : set [0]
  #       # else : append and set [-1]
  #       setIndex = None
  #       if len(self.commandParameters["chirpCfg"]) == 1 and allNone(self.commandParameters["chirpCfg"][0].values()):
  #         setIndex: int = 0
  #       else: 
  #         setIndex: int = len(self.commandParameters["chirpCfg"])
  #         self.commandParameters["chirpCfg"].append(self.commandParameters["chirpCfg"][0].copy())

  #       self.commandParameters["chirpCfg"][setIndex]["chirpStartIndex"] = int(clips.pop(0))
  #       self.commandParameters["chirpCfg"][setIndex]["chirpEndIndex"] = int(clips.pop(0))
  #       self.commandParameters["chirpCfg"][setIndex]["profileIdentifier"] = float(clips.pop(0))
  #       self.commandParameters["chirpCfg"][setIndex]["startFrequencyVariation"] = int(clips.pop(0))
  #       self.commandParameters["chirpCfg"][setIndex]["frequencySlopeVariation"] = float(clips.pop(0))
  #       self.commandParameters["chirpCfg"][setIndex]["idleTimeVariation"] = float(clips.pop(0))
  #       self.commandParameters["chirpCfg"][setIndex]["adcStartTimeVariation"] = float(clips.pop(0))
  #       self.commandParameters["chirpCfg"][setIndex]["txAntennaEnableMask"] = int(clips.pop(0))

  #       # if length >= self.configParameters["numTxAnt"] : delete [0]; config Warn(overflow);
  #       if len(self.commandParameters["chirpCfg"]) > self.configParameters["numTxAnt"]:
  #         del CFG.commandParameters["chirpCfg"][0]
  #         self.logger.log(event="parse_commandParameters", level="Warning", message="For redundant commands (`{commandLine}`), the earliest received commandLine will be removed from the record.".format(commandLine=commandLine))

  #     if self.platform == "xwr16xx":
  #       if main == "bpmCfg": 
  #         self.commandParameters["bpmCfg"]["subFrameIdx"] = int(clips.pop(0))
  #         self.commandParameters["bpmCfg"]["enabled"] = int(clips.pop(0))
  #         self.commandParameters["bpmCfg"]["chirp0Idx"] = int(clips.pop(0))
  #         self.commandParameters["bpmCfg"]["chirp1Idx"] = int(clips.pop(0))
  #     if main == "lowPower": 
  #       self.commandParameters["lowPower"]["dontCare"] = int(clips.pop(0))
  #       self.commandParameters["lowPower"]["adcMode"] = int(clips.pop(0))
  #     if main == "frameCfg": 
  #       self.commandParameters["frameCfg"]["chirpStartIndex"] = int(clips.pop(0))
  #       self.commandParameters["frameCfg"]["chirpEndIndex"] = int(clips.pop(0))
  #       self.commandParameters["frameCfg"]["numberOfLoops"] = int(clips.pop(0))
  #       self.commandParameters["frameCfg"]["numberOfFrames"] = int(clips.pop(0))
  #       self.commandParameters["frameCfg"]["framePeriodicity"] = float(clips.pop(0))
  #       self.commandParameters["frameCfg"]["triggerSelect"] = int(clips.pop(0))
  #       self.commandParameters["frameCfg"]["frameTriggerDelay"] = float(clips.pop(0))
  #       self.parse_configParameters(verificationLevel="Warning")
  #     if self.platform == "xwr16xx":
  #       if main == "advFrameCfg": 
  #         self.commandParameters["advFrameCfg"]["numOfSubFrames"] = int(clips.pop(0))
  #         self.commandParameters["advFrameCfg"]["forceProfile"] = int(clips.pop(0))
  #         self.commandParameters["advFrameCfg"]["numFrames"] = int(clips.pop(0))
  #         self.commandParameters["advFrameCfg"]["triggerSelect"] = int(clips.pop(0))
  #         self.commandParameters["advFrameCfg"]["frameTrigDelay"] = float(clips.pop(0))
  #     if self.platform == "xwr16xx":
  #       if main == "subFrameCfg": 
  #         self.commandParameters["subFrameCfg"]["subFrameNum"] = int(clips.pop(0))
  #         self.commandParameters["subFrameCfg"]["forceProfileIdx"] = int(clips.pop(0))
  #         self.commandParameters["subFrameCfg"]["chirpStartIdx"] = int(clips.pop(0))
  #         self.commandParameters["subFrameCfg"]["numOfChirps"] = int(clips.pop(0))
  #         self.commandParameters["subFrameCfg"]["numLoops"] = int(clips.pop(0))
  #         self.commandParameters["subFrameCfg"]["burstPeriodicity"] = float(clips.pop(0))
  #         self.commandParameters["subFrameCfg"]["chirpStartIdxOffset"] = int(clips.pop(0))
  #         self.commandParameters["subFrameCfg"]["numOfBurst"] = int(clips.pop(0))
  #         self.commandParameters["subFrameCfg"]["numOfBurstLoops"] = int(clips.pop(0))
  #         self.commandParameters["subFrameCfg"]["subFramePeriodicity"] = float(clips.pop(0))
  #     if main == "guiMonitor": 
  #       if self.platform == "xwr16xx":
  #         self.commandParameters["guiMonitor"]["subFrameIdx"] = int(clips.pop(0))
  #       self.commandParameters["guiMonitor"]["detectedObjects"] = int(clips.pop(0))
  #       self.commandParameters["guiMonitor"]["logMagnitudeRange"] = int(clips.pop(0))
  #       self.commandParameters["guiMonitor"]["noiseProfile"] = int(clips.pop(0))
  #       self.commandParameters["guiMonitor"]["rangeAzimuthHeatMap"] = int(clips.pop(0))
  #       self.commandParameters["guiMonitor"]["rangeDopplerHeatMap"] = int(clips.pop(0))
  #       self.commandParameters["guiMonitor"]["statsInfo"] = int(clips.pop(0))
  #     if main == "cfarCfg": 
  #       if self.platform == "xwr16xx":
  #         self.commandParameters["cfarCfg"]["subFrameIdx"] = int(clips.pop(0))
  #       self.commandParameters["cfarCfg"]["procDirection"] = int(clips.pop(0))
  #       self.commandParameters["cfarCfg"]["mode"] = int(clips.pop(0))
  #       self.commandParameters["cfarCfg"]["noiseWin"] = int(clips.pop(0))
  #       self.commandParameters["cfarCfg"]["guardLen"] = int(clips.pop(0))
  #       self.commandParameters["cfarCfg"]["divShift"] = int(clips.pop(0))
  #       self.commandParameters["cfarCfg"]["cyclicModeOrWrappedAroundMode"] = int(clips.pop(0))
  #       self.commandParameters["cfarCfg"]["ThresholdScale"] = int(clips.pop(0))
  #       self.parse_configParameters(verificationLevel="Warning")
  #     if main == "peakGrouping": 
  #       if self.platform == "xwr16xx":
  #         self.commandParameters["peakGrouping"]["subFrameIdx"] = int(clips.pop(0))
  #       self.commandParameters["peakGrouping"]["scheme"] = int(clips.pop(0))
  #       self.commandParameters["peakGrouping"]["peakGroupingInRangeDirection"] = int(clips.pop(0))
  #       self.commandParameters["peakGrouping"]["peakGroupingInDopplerDirection"] = int(clips.pop(0))
  #       self.commandParameters["peakGrouping"]["startRangeIndex"] = int(clips.pop(0))
  #       self.commandParameters["peakGrouping"]["endRangeIndex"] = int(clips.pop(0))
  #     if main == "multiObjBeamForming": 
  #       if self.platform == "xwr16xx":
  #         self.commandParameters["multiObjBeamForming"]["subFrameIdx"] = int(clips.pop(0))
  #       self.commandParameters["multiObjBeamForming"]["featureEnabled"] = int(clips.pop(0))
  #       self.commandParameters["multiObjBeamForming"]["threshold"] = float(clips.pop(0))
  #     if main == "calibDcRangeSig": 
  #       if self.platform == "xwr16xx":
  #         self.commandParameters["calibDcRangeSig"]["subFrameIdx"] = int(clips.pop(0))
  #       self.commandParameters["calibDcRangeSig"]["enabled"] = int(clips.pop(0))
  #       self.commandParameters["calibDcRangeSig"]["negativeBinIdx"] = int(clips.pop(0))
  #       self.commandParameters["calibDcRangeSig"]["positiveBinIdx"] = int(clips.pop(0))
  #       self.commandParameters["calibDcRangeSig"]["numAvg"] = int(clips.pop(0))
  #     if self.platform == "xwr16xx":
  #       if main == "extendedMaxVelocity": 
  #         self.commandParameters["extendedMaxVelocity"]["subFrameIdx"] = int(clips.pop(0))
  #         self.commandParameters["extendedMaxVelocity"]["enabled"] = int(clips.pop(0))
  #     if main == "clutterRemoval": 
  #       self.commandParameters["clutterRemoval"]["enabled"] = int(clips.pop(0))
  #     if main == "compRangeBiasAndRxChanPhase": 
  #       self.commandParameters["compRangeBiasAndRxChanPhase"]["rangeBias"] = float(clips.pop(0))
  #       self.commandParameters["compRangeBiasAndRxChanPhase"]["setOfComplexValue"] = [int(value) for value in clips] # length == self.configParameters["numVirtualAntennas"]
  #       if len(self.commandParameters["compRangeBiasAndRxChanPhase"]["setOfComplexValue"]) == self.configParameters["numVirtualAntennas"]:
  #         self.logger.log(event="parse_commandParameters", level="Error", message="Wrong number of parameters: {commandLine}".format(commandLine=commandLine))
  #     if main == "measureRangeBiasAndRxChanPhase": 
  #       self.commandParameters["measureRangeBiasAndRxChanPhase"]["enabled"] = int(clips.pop(0))
  #       self.commandParameters["measureRangeBiasAndRxChanPhase"]["targetDistance"] = float(clips.pop(0))
  #       self.commandParameters["measureRangeBiasAndRxChanPhase"]["searchWin"] = float(clips.pop(0))
  #     if self.platform == "xwr16xx":
  #       if main == "nearFieldCfg": 
  #         self.commandParameters["nearFieldCfg"]["subFrameIdx"] = int(clips.pop(0))
  #         self.commandParameters["nearFieldCfg"]["enabled"] = int(clips.pop(0))
  #         self.commandParameters["nearFieldCfg"]["startRangeIndex"] = int(clips.pop(0))
  #         self.commandParameters["nearFieldCfg"]["endRangeIndex"] = int(clips.pop(0))
  #     if main == "CQRxSatMonitor": 
  #       self.commandParameters["CQRxSatMonitor"]["profile"] = int(clips.pop(0))
  #       self.commandParameters["CQRxSatMonitor"]["satMonSel"] = int(clips.pop(0))
  #       self.commandParameters["CQRxSatMonitor"]["priSliceDuration"] = int(clips.pop(0))
  #       self.commandParameters["CQRxSatMonitor"]["numSlices"] = int(clips.pop(0))
  #       self.commandParameters["CQRxSatMonitor"]["rxChanMask"] = int(clips.pop(0))
  #     if main == "CQSigImgMonitor": 
  #       self.commandParameters["CQSigImgMonitor"]["profile"] = int(clips.pop(0))
  #       self.commandParameters["CQSigImgMonitor"]["numSlices"] = int(clips.pop(0))
  #       self.commandParameters["CQSigImgMonitor"]["numSamplePerSlice"] = int(clips.pop(0))
  #     if main == "analogMonitor": 
  #       self.commandParameters["analogMonitor"]["rxSaturation"] = int(clips.pop(0))
  #       self.commandParameters["analogMonitor"]["sigImgBand"] = int(clips.pop(0))
  #     if self.platform == "xwr16xx":
  #       if main == "lvdsStreamCfg": 
  #         self.commandParameters["lvdsStreamCfg"]["subFrameIdx"] = int(clips.pop(0))
  #         self.commandParameters["lvdsStreamCfg"]["enableHeader"] = int(clips.pop(0))
  #         self.commandParameters["lvdsStreamCfg"]["dataFmt"] = int(clips.pop(0))
  #         self.commandParameters["lvdsStreamCfg"]["enableSW"] = int(clips.pop(0))
  #     if main == "sensorStop": pass
  #   except: 
  #     self.logger.log(event="parse_commandParameters", level="Error", message="Parse error from: `{commandLine}`".format(commandLine=str(commandLine)))

  # def parse_configParameters_1443(self, verificationLevel="Error"):

  #   def decode_mask(mask: int) -> int:
  #     value = 0
  #     while mask :
  #       mask >>= 1
  #       value += 1
  #     return value

  #   Missing_Command = False

  #   if not Missing_Command: 
  #     try:
  #       self.configParameters["numRxAnt"] = decode_mask(mask=int(self.commandParameters["channelCfg"]["rxChannelEn"]))
  #       self.configParameters["numTxAnt"] = decode_mask(mask=int(self.commandParameters["channelCfg"]["txChannelEn"]))
  #       self.configParameters["numVirtualAntennas"] = self.configParameters["numRxAnt"] * self.configParameters["numTxAnt"]
  #     except TypeError:
  #       Missing_Command = True
  #       self.logger.log(event="parse_configParameters_1443", level=verificationLevel, message="Missing command: `channelCfg`")

  #   if not Missing_Command: 
  #     try:
  #       startFreq = self.commandParameters["profileCfg"]["startFreq"]
  #       idleTime = self.commandParameters["profileCfg"]["idleTime"]
  #       rampEndTime = self.commandParameters["profileCfg"]["rampEndTime"]
  #       freqSlopeConst = self.commandParameters["profileCfg"]["freqSlopeConst"]
  #       numAdcSamples = self.commandParameters["profileCfg"]["numAdcSamples"]
  #       numAdcSamplesRoundTo2 = 1
  #       while numAdcSamples > numAdcSamplesRoundTo2: numAdcSamplesRoundTo2 = numAdcSamplesRoundTo2 << 1
  #       digOutSampleRate = self.commandParameters["profileCfg"]["digOutSampleRate"]
  #     except TypeError:
  #       Missing_Command = True
  #       self.logger.log(event="parse_configParameters_1443", level=verificationLevel, message="Missing command: `profileCfg`")

  #   if not Missing_Command: 
  #     try:
  #       chirpStartIdx = self.commandParameters["frameCfg"]["chirpStartIndex"]
  #       chirpEndIdx = self.commandParameters["frameCfg"]["chirpEndIndex"]
  #       numLoops = self.commandParameters["frameCfg"]["numberOfLoops"]
  #       numFrames = self.commandParameters["frameCfg"]["numberOfFrames"]
  #       self.configParameters["framePeriodicity"] = self.commandParameters["frameCfg"]["framePeriodicity"]
  #       numChirpsPerFrame = (chirpEndIdx - chirpStartIdx + 1) * numLoops
  #     except TypeError:
  #       Missing_Command = True
  #       self.logger.log(event="parse_configParameters_1443", level=verificationLevel, message="Missing command: `frameCfg`")

  #   if not Missing_Command: 
  #     try:
  #       self.configParameters["thresholdScaleDb"] = (self.commandParameters["cfarCfg"]["ThresholdScale"] * 6 * 2**math.ceil(math.log2(self.configParameters["numVirtualAntennas"]))) // (512 * self.configParameters["numVirtualAntennas"])
  #     except TypeError:
  #       Missing_Command = True
  #       self.logger.log(event="parse_configParameters_1443", level=verificationLevel, message="Missing command: `cfarCfg`")

  #   if not Missing_Command: 
  #     self.configParameters["numDopplerBins"] = numChirpsPerFrame / self.configParameters["numTxAnt"]
  #     self.configParameters["numRangeBins"] = numAdcSamplesRoundTo2
  #     self.configParameters["rangeResolutionMeters"] = (3e8 * digOutSampleRate * 1e3) / (2 * freqSlopeConst * 1e12 * numAdcSamples)
  #     self.configParameters["rangeIdxToMeters"] = (3e8 * digOutSampleRate * 1e3) / (2 * freqSlopeConst * 1e12 * self.configParameters["numRangeBins"])
  #     self.configParameters["dopplerResolutionMps"] = 3e8 / (2 * startFreq * 1e9 * (idleTime + rampEndTime) * 1e-6 * self.configParameters["numDopplerBins"] * self.configParameters["numTxAnt"])
  #     self.configParameters["maxRange"] = (300 * 0.9 * digOutSampleRate)/(2 * freqSlopeConst * 1e3)
  #     self.configParameters["maxVelocity"] = 3e8 / (4 * startFreq * 1e9 * (idleTime + rampEndTime) * 1e-6 * self.configParameters["numTxAnt"])
  #     self.logger.log(event="parse_configParameters_1443", level="information", message="parse configParameters success")

  # def parse_configParameters(self, verificationLevel="Error"):

  #   def decode_mask(mask: int) -> int:
  #     value = 0
  #     while mask :
  #       mask >>= 1
  #       value += 1
  #     return value

  #   Missing_Command = False

  #   if not Missing_Command: 
  #     try:
  #       self.configParameters["numRxAnt"] = decode_mask(mask=int(self.commandParameters["channelCfg"]["rxChannelEn"]))
  #       self.configParameters["numTxAnt"] = decode_mask(mask=int(self.commandParameters["channelCfg"]["txChannelEn"]))
  #       self.configParameters["numVirtualAntennas"] = self.configParameters["numRxAnt"] * self.configParameters["numTxAnt"]
  #     except TypeError:
  #       Missing_Command = True
  #       self.logger.log(event="parse_configParameters", level=verificationLevel, message="Missing command: `channelCfg`")

  #   if not Missing_Command: 
  #     try:
  #       startFreq = self.commandParameters["profileCfg"]["startFreq"]
  #       idleTime = self.commandParameters["profileCfg"]["idleTime"]
  #       rampEndTime = self.commandParameters["profileCfg"]["rampEndTime"]
  #       freqSlopeConst = self.commandParameters["profileCfg"]["freqSlopeConst"]
  #       numAdcSamples = self.commandParameters["profileCfg"]["numAdcSamples"]
  #       numAdcSamplesRoundTo2 = 1
  #       while numAdcSamples > numAdcSamplesRoundTo2: numAdcSamplesRoundTo2 = numAdcSamplesRoundTo2 << 1
  #       digOutSampleRate = self.commandParameters["profileCfg"]["digOutSampleRate"]
  #     except TypeError:
  #       Missing_Command = True
  #       self.logger.log(event="parse_configParameters", level=verificationLevel, message="Missing command: `profileCfg`")

  #   if not Missing_Command: 
  #     try:
  #       chirpStartIdx = self.commandParameters["frameCfg"]["chirpStartIndex"]
  #       chirpEndIdx = self.commandParameters["frameCfg"]["chirpEndIndex"]
  #       numLoops = self.commandParameters["frameCfg"]["numberOfLoops"]
  #       numFrames = self.commandParameters["frameCfg"]["numberOfFrames"]
  #       self.configParameters["framePeriodicity"] = self.commandParameters["frameCfg"]["framePeriodicity"]
  #       numChirpsPerFrame = (chirpEndIdx - chirpStartIdx + 1) * numLoops
  #     except TypeError:
  #       Missing_Command = True
  #       self.logger.log(event="parse_configParameters", level=verificationLevel, message="Missing command: `frameCfg`")

  #   if not Missing_Command: 
  #     try:
  #       self.configParameters["thresholdScaleDb"] = (self.commandParameters["cfarCfg"]["ThresholdScale"] * 6 * 2**math.ceil(math.log2(self.configParameters["numVirtualAntennas"]))) // (512 * self.configParameters["numVirtualAntennas"])
  #     except TypeError:
  #       Missing_Command = True
  #       self.logger.log(event="parse_configParameters", level=verificationLevel, message="Missing command: `cfarCfg`")

  #   if not Missing_Command: 
  #     self.configParameters["numDopplerBins"] = numChirpsPerFrame / self.configParameters["numTxAnt"]
  #     self.configParameters["numRangeBins"] = numAdcSamplesRoundTo2
  #     self.configParameters["rangeResolutionMeters"] = (3e8 * digOutSampleRate * 1e3) / (2 * freqSlopeConst * 1e12 * numAdcSamples)
  #     self.configParameters["rangeIdxToMeters"] = (3e8 * digOutSampleRate * 1e3) / (2 * freqSlopeConst * 1e12 * self.configParameters["numRangeBins"])
  #     self.configParameters["dopplerResolutionMps"] = 3e8 / (2 * startFreq * 1e9 * (idleTime + rampEndTime) * 1e-6 * self.configParameters["numDopplerBins"] * self.configParameters["numTxAnt"])
  #     self.configParameters["maxRange"] = (300 * 0.9 * digOutSampleRate)/(2 * freqSlopeConst * 1e3)
  #     self.configParameters["maxVelocity"] = 3e8 / (4 * startFreq * 1e9 * (idleTime + rampEndTime) * 1e-6 * self.configParameters["numTxAnt"])
  #     self.logger.log(event="parse_configParameters", level="information", message="parse configParameters success")

  # # def calc_CfarRangeThreshold_dB_1443(self, threshold_dB: int|float):
  # #   if threshold_dB<0 or threshold_dB>100: 
  # #     return self.commandParameters["cfarCfg"]["ThresholdScale"]
  # #   return (threshold_dB * 512 * self.configParameters["numVirtualAntennas"]) // (6 * 2**math.ceil(math.log2(self.configParameters["numVirtualAntennas"])))

  # def set_CfarRangeThreshold_dB(self, threshold_dB: int|float):
  #   if threshold_dB<0 or threshold_dB>100: 
  #     return
  #   if self.platform == "xWR14xx":
  #     self.commandParameters["cfarCfg"]["ThresholdScale"] = (threshold_dB * 512 * self.configParameters["numVirtualAntennas"]) // (6 * 2**math.ceil(math.log2(self.configParameters["numVirtualAntennas"])))
  #   if self.platform == "xWR16xx":
  #     self.commandParameters["cfarCfg"]["ThresholdScale"] = (threshold_dB * 256 * self.configParameters["numVirtualAntennas"]) // 6

  # def set_RemoveStaticClutter(self, enabled: bool):
  #   self.commandParameters["clutterRemoval"]["enabled"] = int(enabled)

  # def set_FramePeriodicity(self, milliseconds: int|float):
  #   self.commandParameters["frameCfg"]["framePeriodicity"] = milliseconds
  #   self.configParameters["framePeriodicity"] = milliseconds
  
  # # def command_CfarRangeThreshold_dB_1443(self, threshold_dB: int|float) -> str:
  # #   self.commandParameters["cfarCfg"]["ThresholdScale"] = self.calc_CfarRangeThreshold_dB_1443(threshold_dB)
  # #   return ' '.join(["cfarCfg", 
  # #           str(self.commandParameters["cfarCfg"]["procDirection"]), 
  # #           str(self.commandParameters["cfarCfg"]["mode"]), 
  # #           str(self.commandParameters["cfarCfg"]["noiseWin"]), 
  # #           str(self.commandParameters["cfarCfg"]["guardLen"]), 
  # #           str(self.commandParameters["cfarCfg"]["divShift"]), 
  # #           str(self.commandParameters["cfarCfg"]["cyclicModeOrWrappedAroundMode"]), 
  # #           str(self.commandParameters["cfarCfg"]["ThresholdScale"])
  # #           ])
  
  # # def command_RemoveStaticClutter(self, enabled: bool = True) -> str:
  # #   self.commandParameters["clutterRemoval"]["enabled"] = int(enabled)
  # #   return ' '.join(["clutterRemoval", str(self.commandParameters["clutterRemoval"]["enabled"])])

  # def command_Generator(self, command: str, end: str='\n') -> str:
  #   # print("command_Generator('{}'):".format(command), self.commandParameters[command], '\n')
  #   commandLine = command
  #   if command == "sensorStart": 
  #     if self.commandParameters["sensorStart"]["doReconfig"] != None:
  #       commandLine += ' ' + str(self.commandParameters["sensorStart"]["doReconfig"])
  #   if command == "flushCfg": pass
  #   if command == "dfeDataOutputMode": 
  #     commandLine += ' ' + str(self.commandParameters["dfeDataOutputMode"]["modeType"])
  #   if command == "channelCfg": 
  #     commandLine += ' ' + str(self.commandParameters["channelCfg"]["rxChannelEn"])
  #     commandLine += ' ' + str(self.commandParameters["channelCfg"]["txChannelEn"])
  #     commandLine += ' ' + str(self.commandParameters["channelCfg"]["cascading"])
  #   if command == "adcCfg": 
  #     commandLine += ' ' + str(self.commandParameters["adcCfg"]["numADCBits"])
  #     commandLine += ' ' + str(self.commandParameters["adcCfg"]["adcOutputFmt"])
  #   if command == "adcbufCfg": 
  #     if self.platform == "xwr16xx":
  #       commandLine += ' ' + str(self.commandParameters["adcbufCfg"]["subFrameIdx"])
  #     commandLine += ' ' + str(self.commandParameters["adcbufCfg"]["adcOutputFmt"])
  #     commandLine += ' ' + str(self.commandParameters["adcbufCfg"]["SampleSwap"])
  #     commandLine += ' ' + str(self.commandParameters["adcbufCfg"]["ChanInterleave"])
  #     commandLine += ' ' + str(self.commandParameters["adcbufCfg"]["ChirpThreshold"])
  #   if command == "profileCfg": 
  #     commandLine += ' ' + str(self.commandParameters["profileCfg"]["profileId"])
  #     commandLine += ' ' + str(self.commandParameters["profileCfg"]["startFreq"])
  #     commandLine += ' ' + str(self.commandParameters["profileCfg"]["idleTime"])
  #     commandLine += ' ' + str(self.commandParameters["profileCfg"]["adcStartTime"])
  #     commandLine += ' ' + str(self.commandParameters["profileCfg"]["rampEndTime"])
  #     commandLine += ' ' + str(self.commandParameters["profileCfg"]["txOutPower"])
  #     commandLine += ' ' + str(self.commandParameters["profileCfg"]["txPhaseShifter"])
  #     commandLine += ' ' + str(self.commandParameters["profileCfg"]["freqSlopeConst"])
  #     commandLine += ' ' + str(self.commandParameters["profileCfg"]["txStartTime"])
  #     commandLine += ' ' + str(self.commandParameters["profileCfg"]["numAdcSamples"])
  #     commandLine += ' ' + str(self.commandParameters["profileCfg"]["digOutSampleRate"])
  #     commandLine += ' ' + str(self.commandParameters["profileCfg"]["hpfCornerFreq1"])
  #     commandLine += ' ' + str(self.commandParameters["profileCfg"]["hpfCornerFreq2"])
  #     commandLine += ' ' + str(self.commandParameters["profileCfg"]["rxGain"])
  #   if command == "chirpCfg": 
  #     chirpCfg_index = 0
  #     while chirpCfg_index < self.configParameters["numTxAnt"]:
  #       if chirpCfg_index != 0: commandLine += end + "chirpCfg"
  #       commandLine += ' ' + str(self.commandParameters["chirpCfg"][chirpCfg_index]["chirpStartIndex"])
  #       commandLine += ' ' + str(self.commandParameters["chirpCfg"][chirpCfg_index]["chirpEndIndex"])
  #       commandLine += ' ' + str(self.commandParameters["chirpCfg"][chirpCfg_index]["profileIdentifier"])
  #       commandLine += ' ' + str(self.commandParameters["chirpCfg"][chirpCfg_index]["startFrequencyVariation"])
  #       commandLine += ' ' + str(self.commandParameters["chirpCfg"][chirpCfg_index]["frequencySlopeVariation"])
  #       commandLine += ' ' + str(self.commandParameters["chirpCfg"][chirpCfg_index]["idleTimeVariation"])
  #       commandLine += ' ' + str(self.commandParameters["chirpCfg"][chirpCfg_index]["adcStartTimeVariation"])
  #       commandLine += ' ' + str(self.commandParameters["chirpCfg"][chirpCfg_index]["txAntennaEnableMask"])
  #       chirpCfg_index += 1
  #   if self.platform == "xwr16xx":
  #     if command == "bpmCfg": 
  #       commandLine += ' ' + str(self.commandParameters["bpmCfg"]["subFrameIdx"])
  #       commandLine += ' ' + str(self.commandParameters["bpmCfg"]["enabled"])
  #       commandLine += ' ' + str(self.commandParameters["bpmCfg"]["chirp0Idx"])
  #       commandLine += ' ' + str(self.commandParameters["bpmCfg"]["chirp1Idx"])
  #   if command == "lowPower": 
  #     commandLine += ' ' + str(self.commandParameters["lowPower"]["dontCare"])
  #     commandLine += ' ' + str(self.commandParameters["lowPower"]["adcMode"])
  #   if command == "frameCfg": 
  #     commandLine += ' ' + str(self.commandParameters["frameCfg"]["chirpStartIndex"])
  #     commandLine += ' ' + str(self.commandParameters["frameCfg"]["chirpEndIndex"])
  #     commandLine += ' ' + str(self.commandParameters["frameCfg"]["numberOfLoops"])
  #     commandLine += ' ' + str(self.commandParameters["frameCfg"]["numberOfFrames"])
  #     commandLine += ' ' + str(self.commandParameters["frameCfg"]["framePeriodicity"])
  #     commandLine += ' ' + str(self.commandParameters["frameCfg"]["triggerSelect"])
  #     commandLine += ' ' + str(self.commandParameters["frameCfg"]["frameTriggerDelay"])
  #   if self.platform == "xwr16xx":
  #     if command == "advFrameCfg": 
  #       commandLine += ' ' + str(self.commandParameters["advFrameCfg"]["numOfSubFrames"])
  #       commandLine += ' ' + str(self.commandParameters["advFrameCfg"]["forceProfile"])
  #       commandLine += ' ' + str(self.commandParameters["advFrameCfg"]["numFrames"])
  #       commandLine += ' ' + str(self.commandParameters["advFrameCfg"]["triggerSelect"])
  #       commandLine += ' ' + str(self.commandParameters["advFrameCfg"]["frameTrigDelay"])
  #   if self.platform == "xwr16xx":
  #     if command == "subFrameCfg": 
  #       commandLine += ' ' + str(self.commandParameters["subFrameCfg"]["subFrameNum"])
  #       commandLine += ' ' + str(self.commandParameters["subFrameCfg"]["forceProfileIdx"])
  #       commandLine += ' ' + str(self.commandParameters["subFrameCfg"]["chirpStartIdx"])
  #       commandLine += ' ' + str(self.commandParameters["subFrameCfg"]["numOfChirps"])
  #       commandLine += ' ' + str(self.commandParameters["subFrameCfg"]["numLoops"])
  #       commandLine += ' ' + str(self.commandParameters["subFrameCfg"]["burstPeriodicity"])
  #       commandLine += ' ' + str(self.commandParameters["subFrameCfg"]["chirpStartIdxOffset"])
  #       commandLine += ' ' + str(self.commandParameters["subFrameCfg"]["numOfBurst"])
  #       commandLine += ' ' + str(self.commandParameters["subFrameCfg"]["numOfBurstLoops"])
  #       commandLine += ' ' + str(self.commandParameters["subFrameCfg"]["subFramePeriodicity"])
  #   if command == "guiMonitor": 
  #     if self.platform == "xwr16xx":
  #       commandLine += ' ' + str(self.commandParameters["guiMonitor"]["subFrameIdx"])
  #     commandLine += ' ' + str(self.commandParameters["guiMonitor"]["detectedObjects"])
  #     commandLine += ' ' + str(self.commandParameters["guiMonitor"]["logMagnitudeRange"])
  #     commandLine += ' ' + str(self.commandParameters["guiMonitor"]["noiseProfile"])
  #     commandLine += ' ' + str(self.commandParameters["guiMonitor"]["rangeAzimuthHeatMap"])
  #     commandLine += ' ' + str(self.commandParameters["guiMonitor"]["rangeDopplerHeatMap"])
  #     commandLine += ' ' + str(self.commandParameters["guiMonitor"]["statsInfo"])
  #   if command == "cfarCfg": 
  #     if self.platform == "xwr16xx":
  #       commandLine += ' ' + str(self.commandParameters["cfarCfg"]["subFrameIdx"])
  #     commandLine += ' ' + str(self.commandParameters["cfarCfg"]["procDirection"])
  #     commandLine += ' ' + str(self.commandParameters["cfarCfg"]["mode"])
  #     commandLine += ' ' + str(self.commandParameters["cfarCfg"]["noiseWin"])
  #     commandLine += ' ' + str(self.commandParameters["cfarCfg"]["guardLen"])
  #     commandLine += ' ' + str(self.commandParameters["cfarCfg"]["divShift"])
  #     commandLine += ' ' + str(self.commandParameters["cfarCfg"]["cyclicModeOrWrappedAroundMode"])
  #     commandLine += ' ' + str(self.commandParameters["cfarCfg"]["ThresholdScale"])
  #   if command == "peakGrouping": 
  #     if self.platform == "xwr16xx":
  #       commandLine += ' ' + str(self.commandParameters["peakGrouping"]["subFrameIdx"])
  #     commandLine += ' ' + str(self.commandParameters["peakGrouping"]["scheme"])
  #     commandLine += ' ' + str(self.commandParameters["peakGrouping"]["peakGroupingInRangeDirection"])
  #     commandLine += ' ' + str(self.commandParameters["peakGrouping"]["peakGroupingInDopplerDirection"])
  #     commandLine += ' ' + str(self.commandParameters["peakGrouping"]["startRangeIndex"])
  #     commandLine += ' ' + str(self.commandParameters["peakGrouping"]["endRangeIndex"])
  #   if command == "multiObjBeamForming": 
  #     if self.platform == "xwr16xx":
  #       commandLine += ' ' + str(self.commandParameters["multiObjBeamForming"]["subFrameIdx"])
  #     commandLine += ' ' + str(self.commandParameters["multiObjBeamForming"]["featureEnabled"])
  #     commandLine += ' ' + str(self.commandParameters["multiObjBeamForming"]["threshold"])
  #   if self.platform == "xwr16xx":
  #     if command == "calibDcRangeSig": 
  #       commandLine += ' ' + str(self.commandParameters["calibDcRangeSig"]["subFrameIdx"])
  #       commandLine += ' ' + str(self.commandParameters["calibDcRangeSig"]["enabled"])
  #       commandLine += ' ' + str(self.commandParameters["calibDcRangeSig"]["negativeBinIdx"])
  #       commandLine += ' ' + str(self.commandParameters["calibDcRangeSig"]["positiveBinIdx"])
  #       commandLine += ' ' + str(self.commandParameters["calibDcRangeSig"]["numAvg"])
  #   if self.platform == "xwr16xx":
  #     if command == "extendedMaxVelocity": 
  #       commandLine += ' ' + str(self.commandParameters["extendedMaxVelocity"]["subFrameIdx"])
  #       commandLine += ' ' + str(self.commandParameters["extendedMaxVelocity"]["enabled"])
  #   if command == "clutterRemoval": 
  #     commandLine += ' ' + str(self.commandParameters["clutterRemoval"]["enabled"])
  #   if command == "compRangeBiasAndRxChanPhase": 
  #     commandLine += ' ' + str(self.commandParameters["compRangeBiasAndRxChanPhase"]["rangeBias"])
  #     commandLine += ' ' + ' '.join(map(str, self.commandParameters["compRangeBiasAndRxChanPhase"]["setOfComplexValue"]))
  #   if command == "measureRangeBiasAndRxChanPhase": 
  #     commandLine += ' ' + str(self.commandParameters["measureRangeBiasAndRxChanPhase"]["enabled"])
  #     commandLine += ' ' + str(self.commandParameters["measureRangeBiasAndRxChanPhase"]["targetDistance"])
  #     commandLine += ' ' + str(self.commandParameters["measureRangeBiasAndRxChanPhase"]["searchWin"])
  #   if self.platform == "xwr16xx":
  #     if command == "nearFieldCfg": 
  #       commandLine += ' ' + str(self.commandParameters["nearFieldCfg"]["subFrameIdx"])
  #       commandLine += ' ' + str(self.commandParameters["nearFieldCfg"]["enabled"])
  #       commandLine += ' ' + str(self.commandParameters["nearFieldCfg"]["startRangeIndex"])
  #       commandLine += ' ' + str(self.commandParameters["nearFieldCfg"]["endRangeIndex"])
  #   if command == "CQRxSatMonitor": 
  #     commandLine += ' ' + str(self.commandParameters["CQRxSatMonitor"]["profile"])
  #     commandLine += ' ' + str(self.commandParameters["CQRxSatMonitor"]["satMonSel"])
  #     commandLine += ' ' + str(self.commandParameters["CQRxSatMonitor"]["priSliceDuration"])
  #     commandLine += ' ' + str(self.commandParameters["CQRxSatMonitor"]["numSlices"])
  #     commandLine += ' ' + str(self.commandParameters["CQRxSatMonitor"]["rxChanMask"])
  #   if command == "CQSigImgMonitor": 
  #     commandLine += ' ' + str(self.commandParameters["CQSigImgMonitor"]["profile"])
  #     commandLine += ' ' + str(self.commandParameters["CQSigImgMonitor"]["numSlices"])
  #     commandLine += ' ' + str(self.commandParameters["CQSigImgMonitor"]["numSamplePerSlice"])
  #   if command == "analogMonitor": 
  #     commandLine += ' ' + str(self.commandParameters["analogMonitor"]["rxSaturation"])
  #     commandLine += ' ' + str(self.commandParameters["analogMonitor"]["sigImgBand"])
  #   if self.platform == "xwr16xx":
  #     if command == "lvdsStreamCfg": 
  #       commandLine += ' ' + str(self.commandParameters["lvdsStreamCfg"]["subFrameIdx"])
  #       commandLine += ' ' + str(self.commandParameters["lvdsStreamCfg"]["enableHeader"])
  #       commandLine += ' ' + str(self.commandParameters["lvdsStreamCfg"]["dataFmt"])
  #       commandLine += ' ' + str(self.commandParameters["lvdsStreamCfg"]["enableSW"])
  #   if command == "sensorStop": pass
  #   return commandLine + end

# %%
if __name__ == '__main__':
  CFG = Configuration_2_1_0(platform="xWR14xx")