#!/usr/bin/python
import sys
import fsf_header as fsf

nev = fsf.EVS_ORIG

def main(argv):
    fsf_str = ""

    fsf_str += "\n# FEAT version number"
    fsf_str += "\nset fmri(version) %1.2f\n" % fsf.VERSION

    fsf_str += "\n# Are we in MELODIC?"
    fsf_str += "\nset fmri(inmelodic) %d\n" % fsf.INMELODIC

    fsf_str += "\n# Analysis level"
    fsf_str += "\n# 1 : First-level analysis"
    fsf_str += "\n# 2 : Higher-level analysis"
    fsf_str += "\nset fmri(level) %d\n" % fsf.LEVEL

    fsf_str += "\n# Which stages to run"
    fsf_str += "\n# 0 : No first-level analysis (registration and/or group stats only)"
    fsf_str += "\n# 7 : Full first-level analysis"
    fsf_str += "\n# 1 : Pre-processing"
    fsf_str += "\n# 2 : Statistics"
    fsf_str += "\nset fmri(analysis) %d\n" % fsf.ANALYSIS

    if fsf.VERSION == 5.4:
        fsf_str += "\n# Delay before starting (hours)"
        fsf_str += "set fmri(delay) %d\n" % fsf.DELAY

    fsf_str += "\n# Use relative filenames"
    fsf_str += "\nset fmri(relative_yn) %d\n" % fsf.RELATIVE_YN

    fsf_str += "\n# Balloon help"
    fsf_str += "\nset fmri(help_yn) %d\n" % fsf.HELP_YN

    fsf_str += "\n# Run Featwatcher"
    fsf_str += "\nset fmri(featwatcher_yn) %d\n" % fsf.FEATWATCHER_YN

    fsf_str += "\n# Cleanup first-level standard-space images"
    fsf_str += "\nset fmri(sscleanup_yn) %d\n" % fsf.SSCLEANUP_YN

    fsf_str += "\n# Output directory"
    fsf_str += "\nset fmri(outputdir) %s\n" % fsf.OUTPUTDIR

    fsf_str += "\n# TR(s)"
    fsf_str += "\nset fmri(tr) %1.1f\n" % fsf.TR

    fsf_str += "\n# Total volumes"
    fsf_str += "\nset fmri(npts) %d\n" % fsf.NPTS

    fsf_str += "\n# Delete volumes"
    fsf_str += "\nset fmri(ndelete) %d\n" % fsf.NDELETE

    if fsf.VERSION >= 5.98:
        fsf_str += "\n# Perfusion tag/control order"
        fsf_str += "\nset fmri(tagfirst) %d\n" % fsf.TAGFIRST

    fsf_str += "\n# Number of first-level analyses"
    fsf_str += "\nset fmri(multiple) %d\n" % fsf.MULTIPLE

    fsf_str += "\n# Higher-level input type"
    fsf_str += "\n# 1 : Inputs are lower-level FEAT directories"
    fsf_str += "\n# 2 : Inputs are cope images from FEAT directories"
    fsf_str += "\nset fmri(inputtype) %d\n" % fsf.INPUTTYPE

    fsf_str += "\n# Carry out pre-stats processing?"
    fsf_str += "\nset fmri(filtering_yn) %d\n" % fsf.FILTERING_YN

    fsf_str += "\n# Brain/background threshold, %"
    fsf_str += "\nset fmri(brain_thresh) %d\n" % fsf.BRAIN_THRESH

    if fsf.VERSION >= 5.98:
        fsf_str += "\n# Critical z for design efficiency calculation"
        fsf_str += "\nset fmri(critical_z) %1.1f\n" % fsf.CRITICAL_Z

        fsf_str += "\n# Noise level"
        fsf_str += "\nset fmri(noise) %1.2f\n" % fsf.NOISE
        fsf_str += "\n# Noise AR(1)"
        fsf_str += "\nset fmri(noisear) %1.2f\n" % fsf.NOISEAR

    fsf_str += "\n# Motion correction"
    fsf_str += "\n# 0 : None"
    fsf_str += "\n# 1 : MCFLIRT"
    fsf_str += "\nset fmri(mc) %d\n" % fsf.MC

    fsf_str += "\n# Spin-history (currently obsolete)"
    fsf_str += "\nset fmri(sh_yn) %d\n" % fsf.SH_YN

    fsf_str += "\n# B0 fieldmap unwarping?"
    fsf_str += "\nset fmri(regunwarp_yn) %d\n" % fsf.REGUNWARP_YN

    if fsf.VERSION >= 5.98:
        fsf_str += "\n# EPI dwell time (ms)"
        fsf_str += "\nset fmri(dwell) %1.1f\n" % fsf.DWELL

        fsf_str += "\n# EPI TE (ms)"
        fsf_str += "\nset fmri(te) %d\n" % fsf.TE

        fsf_str += "\n# % Signal loss threshold"
        fsf_str += "\nset fmri(signallossthresh) %d\n" % fsf.SIGNALLOSSTHRESH

        fsf_str += "\n# Unwarp direction"
        fsf_str += "\nset fmri(unwarp_dir) %s\n" % fsf.UNWARP_DIR

    if fsf.VERSION == 5.4:
        fsf_str += "\n# Dwell/Asymmetry ratio "
        fsf_str += "\nset fmri(dwellasym) %d\n" % fsf.DWELLASYM

    """fsf_str += "\n# Post-stats-only directory copying"
    fsf_str += "\n# 0 : Overwrite original post-stats results"
    fsf_str += "\n# 1 : Copy original FEAT directory for new Contrasts, Thresholding, Rendering"
    fsf_str += "\nset fmri(newdir_yn) %d\n" % fsf.NEWDIR_YN
"""
    fsf_str += "\n# Slice timing correction"
    fsf_str += "\n# 0 : None"
    fsf_str += "\n# 1 : Regular up (0, 1, 2, 3, ...)"
    fsf_str += "\n# 2 : Regular down"
    fsf_str += "\n# 3 : Use slice order file"
    fsf_str += "\n# 4 : Use slice timings file"
    fsf_str += "\n# 5 : Interleaved (0, 2, 4 ... 1, 3, 5 ... )"
    fsf_str += "\nset fmri(st) %d\n" % fsf.ST

    fsf_str += "\n# Slice timings file"
    fsf_str += "\nset fmri(st_file) %s\n" % fsf.ST_FILE

    fsf_str += "\n# BET brain extraction"
    fsf_str += "\nset fmri(bet_yn) %d\n" % fsf.BET_YN

    fsf_str += "\n# Spatial smoothing FWHM (mm)"
    fsf_str += "\nset fmri(smooth) %d\n" % fsf.SMOOTH

    fsf_str += "\n# Intensity normalization"
    fsf_str += "\nset fmri(norm_yn) %d\n" % fsf.NORM_YN

    if fsf.VERSION >= 5.98:
        fsf_str += "\n# Perfusion subtraction"
        fsf_str += "\nset fmri(perfsub_yn) %d\n" % fsf.PERFSUB_YN

    fsf_str += "\n# Highpass temporal filtering"
    fsf_str += "\nset fmri(temphp_yn) %d\n" % fsf.TEMPHP_YN

    fsf_str += "\n# Lowpass temporal filtering"
    fsf_str += "\nset fmri(templp_yn) %d\n" % fsf.TEMPLP_YN

    fsf_str += "\n# MELODIC ICA data exploration"
    fsf_str += "\nset fmri(melodic_yn) %d\n" % fsf.MELODIC_YN

    fsf_str += "\n# Carry out main stats?"
    fsf_str += "\nset fmri(stats_yn) %d\n" % fsf.STATS_YN

    fsf_str += "\n# Carry out prewhitening?"
    fsf_str += "\nset fmri(prewhiten_yn) %d\n" % fsf.PREWHITEN_YN

    if fsf.VERSION >= 5.98:
        fsf_str += "\n# Add motion parameters to model"
        fsf_str += "\n# 0 : No"
        fsf_str += "\n# 1 : Yes"
        fsf_str += "\nset fmri(motionevs) %d" % fsf.MOTIONEVS
        fsf_str += "\nset fmri(motionevsbeta) %s" % fsf.MOTIONEVSBETA
        fsf_str += "\nset fmri(scriptevsbeta) %s\n" % fsf.SCRIPTEVSBETA

    fsf_str += "\n# Robust outlier detection in FLAME?"
    fsf_str += "\nset fmri(robust_yn) %d\n" % fsf.ROBUST_YN

    fsf_str += "\n# Higher-level modelling"
    fsf_str += "\n# 3 : Fixed effects"
    fsf_str += "\n# 0 : Mixed Effects: Simple OLS"
    fsf_str += "\n# 2 : Mixed Effects: FLAME 1"
    fsf_str += "\n# 1 : Mixed Effects: FLAME 1+2"
    fsf_str += "\nset fmri(mixed_yn) %d\n" % fsf.MIXED_YN

    fsf_str += "\n# Number of EVs"
    fsf_str += "\nset fmri(evs_orig) %d" % fsf.EVS_ORIG
    fsf_str += "\nset fmri(evs_real) %d" % fsf.EVS_REAL
    if fsf.VERSION >= 5.98:
        fsf_str += "\nset fmri(evs_vox) %d\n" % fsf.EVS_VOX
    else:
        fsf_str += "\n"

    fsf_str += "\n# Number of contrasts"
    fsf_str += "\nset fmri(ncon_orig) %d" % fsf.NCON_ORIG
    fsf_str += "\nset fmri(ncon_real) %d\n" % fsf.NCON_REAL

    fsf_str += "\n# Number of F-tests"
    fsf_str += "\nset fmri(nftests_orig) %d" % fsf.NFTESTS_ORIG
    fsf_str += "\nset fmri(nftests_real) %d\n" % fsf.NFTESTS_REAL

    fsf_str += "\n# Add constant column to design matrix? (obsolete)"
    fsf_str += "\nset fmri(constcol) %d\n" % fsf.CONSTCOL

    fsf_str += "\n# Carry out post-stats steps?"
    fsf_str += "\nset fmri(poststats_yn) %d\n" % fsf.POSTSTATS_YN
    
    fsf_str += "\n# Pre-threshold masking?"
    fsf_str += "\nset fmri(threshmask) %s\n" % fsf.THRESHMASK
    
    fsf_str += "\n# Thresholding"
    fsf_str += "\n# 0 : None"
    fsf_str += "\n# 1 : Uncorrected"
    fsf_str += "\n# 2 : Voxel"
    fsf_str += "\n# 3 : Cluster"
    fsf_str += "\nset fmri(thresh) %d\n" % fsf.THRESH
    
    fsf_str += "\n# P threshold"
    fsf_str += "\nset fmri(prob_thresh) %1.2f\n" % fsf.PROB_THRESH

    fsf_str += "\n# Z threshold"
    fsf_str += "\nset fmri(z_thresh) %1.1f\n" % fsf.Z_THRESH

    fsf_str += "\n# Z min/max for colour rendering"
    fsf_str += "\n# 0 : Use actual Z min/max"
    fsf_str += "\n# 1 : Use preset Z min/max"
    fsf_str += "\nset fmri(zdisplay) %d\n" % fsf.ZDISPLAY

    fsf_str += "\n# Z min in colour rendering"
    fsf_str += "\nset fmri(zmin) %d\n" % fsf.ZMIN

    fsf_str += "\n# Z max in colour rendering"
    fsf_str += "\nset fmri(zmax) %d\n" % fsf.ZMAX
    
    fsf_str += "\n# Colour rendering type"
    fsf_str += "\n# 0 : Solid blobs"
    fsf_str += "\n# 1 : Transparent blobs"
    fsf_str += "\nset fmri(rendertype) %d\n" % fsf.RENDERTYPE

    fsf_str += "\n# Background image for higher-level stats overlays"
    fsf_str += "\n# 1 : Mean highres"
    fsf_str += "\n# 2 : First highres"
    fsf_str += "\n# 3 : Mean functional"
    fsf_str += "\n# 4 : First functional"
    fsf_str += "\n# 5 : Standard space template"
    fsf_str += "\nset fmri(bgimage) %d\n" % fsf.BGIMAGE

    if fsf.VERSION >= 5.98:
        fsf_str += "\n# Create time series plots"
        fsf_str += "\nset fmri(tsplot_yn) %d\n" % fsf.TSPLOT_YN

    """fsf_str += "\n# Registration?"
    fsf_str += "\nset fmri(reg_yn) %d\n" % fsf.REG_YN
"""
    fsf_str += "\n# Registration to initial structural"
    fsf_str += "\nset fmri(reginitial_highres_yn) %d\n" % fsf.REGINITIAL_HIGHRES_YN

    fsf_str += "\n# Search space for registration to initial structural"
    fsf_str += "\n# 0   : No search"
    fsf_str += "\n# 90  : Normal search"
    fsf_str += "\n# 180 : Full search"
    fsf_str += "\nset fmri(reginitial_highres_search) %d\n" % fsf.REGINITIAL_HIGHRES_SEARCH

    fsf_str += "\n# Degrees of Freedom for registration to initial structural"
    fsf_str += "\nset fmri(reginitial_highres_dof) %d\n" % fsf.REGINITIAL_HIGHRES_DOF

    if fsf.VERSION == 5.4:
        fsf_str += "\n# Do nonlinear registration to initial structural?"
        fsf_str += "\nset fmri(reginitial_highres_nonlinear_yn) %d\n" % fsf.REGINITIAL_HIGHRES_NONLINEAR_YN

    fsf_str += "\n# Registration to main structural"
    fsf_str += "\nset fmri(reghighres_yn) %d\n" % fsf.REGHIGHRES_YN

    fsf_str += "\n# Search space for registration to main structural"
    fsf_str += "\n# 0   : No search"
    fsf_str += "\n# 90  : Normal search"
    fsf_str += "\n# 180 : Full search"
    fsf_str += "\nset fmri(reghighres_search) %d\n" % fsf.REGHIGHRES_SEARCH

    fsf_str += "\n# Degrees of Freedom for registration to main structural"
    fsf_str += "\nset fmri(reghighres_dof) %s\n" % fsf.REGHIGHRES_DOF

    if fsf.VERSION == 5.4:
        fsf_str += "\n# Do nonlinear registration to main structural?"
        fsf_str += "\nset fmri(reghighres_nonlinear_yn) %d\n" % fsf.REGHIGHRES_NONLINEAR_YN

    fsf_str += "\n# Registration to standard image?"
    fsf_str += "\nset fmri(regstandard_yn) %d\n" % fsf.REGSTANDARD_YN

    fsf_str += "\n# Use alternate reference images?"
    fsf_str += "\nset fmri(alternateReference_yn) %d\n" % fsf.ALTERNATEREFERENCE_YN

    fsf_str += "\n# Standard image"
    fsf_str += "\nset fmri(regstandard) %s\n" % fsf.REGSTANDARD

    fsf_str += "\n# Search space for registration to standard space"
    fsf_str += "\n# 0   : No search"
    fsf_str += "\n# 90  : Normal search"
    fsf_str += "\n# 180 : Full search"
    fsf_str += "\nset fmri(regstandard_search) %d\n" % fsf.REGSTANDARD_SEARCH

    fsf_str += "\n# Degrees of Freedom for registration to standard space"
    fsf_str += "\nset fmri(regstandard_dof) %d\n" % fsf.REGSTANDARD_DOF

    fsf_str += "\n# Do nonlinear registration from structural to standard space?"
    fsf_str += "\nset fmri(regstandard_nonlinear_yn) %d\n" % fsf.REGSTANDARD_NONLINEAR_YN

    if fsf.VERSION >= 5.98:
        fsf_str += "\n# Control nonlinear warp field resolution"
        fsf_str += "\nset fmri(regstandard_nonlinear_warpres) %d \n" % fsf.REGSTANDARD_NONLINEAR_WARPRES

    fsf_str += "\n# High pass filter cutoff"
    fsf_str += "\nset fmri(paradigm_hp) %d\n" % fsf.PARADIGM_HP

    fsf_str += "\n# Number of lower-level copes feeding into higher-level analysis"
    fsf_str += "\nset fmri(ncopeinputs) %d\n" % fsf.NCOPEINPUTS

    for i in range(fsf.NCOPEINPUTS):
        fsf_str += "\n# Use lower-level cope %d for higher-level analysis" % (i+1)
        fsf_str += "\nset fmri(copeinput.%d) %d\n" % ((i+1), fsf.COPEINPUT[i])

    for i in range(fsf.MULTIPLE):
        fsf_str += "\n# 4D AVW data or FEAT directory (%d)" % (i+1)
        fsf_str += "\nset feat_files(%d) %s\n" % ((i+1), fsf.FEAT_FILES[i])

    fsf_str += "\n# Add confound EVs text file"
    fsf_str += "\nset fmri(confoundevs) %d\n" % fsf.CONFOUNDEVS

    if fsf.REGINITIAL_HIGHRES_YN == 1:
        for i in range(fsf.MULTIPLE):
            fsf_str += "\n# Session's structural image for analysis %d" % (i+1)
            fsf_str += "\nset initial_highres_files(%d) %s\n" % ((i+1), fsf.INITIAL_HIGHRES_FILES[i])

    if fsf.REGHIGHRES_YN == 1:
        for i in range(fsf.MULTIPLE):
            fsf_str += "\n# Subject's structural image for analysis %d" % (i+1)
            fsf_str += "\nset highres_files(%d) %s\n" % ((i+1), fsf.HIGHRES_FILES[i])

    for i in range(nev):
        if fsf.VERSION >= 5.98:
            fsf_str += "\n# EV %d title" % (i+1)
            fsf_str += "\nset fmri(evtitle%d) %s\n" % ((i+1), fsf.EVTITLE[i])

        fsf_str += "\n# Basic waveform shape (EV %d)" % (i+1)
        fsf_str += "\n# 0 : Square"
        fsf_str += "\n# 1 : Sinusoid"
        fsf_str += "\n# 2 : Custom (1 entry per volume)"
        fsf_str += "\n# 3 : Custom (3 column format)"
        fsf_str += "\n# 4 : Interaction"
        fsf_str += "\n# 10 : Empty (all zeros)"
        fsf_str += "\nset fmri(shape%d) %d\n" % ((i+1), fsf.SHAPE[i])

        fsf_str += "\n# Convolution (EV %d)" % (i+1)
        fsf_str += "\n# 0 : None"
        fsf_str += "\n# 1 : Gaussian"
        fsf_str += "\n# 2 : Gamma"
        fsf_str += "\n# 3 : Double-Gamma HRF"
        fsf_str += "\n# 4 : Gamma basis functions"
        fsf_str += "\n# 5 : Sine basis functions"
        fsf_str += "\n# 6 : FIR basis functions"
        fsf_str += "\nset fmri(convolve%d) %d\n" % ((i+1), fsf.CONVOLVE[i])

        fsf_str += "\n# Convolve phase (EV %d)" % (i+1)
        fsf_str += "\nset fmri(convolve_phase%d) %d\n" % ((i+1), fsf.CONVOLVE_PHASE[i])

        fsf_str += "\n# Apply temporal filtering (EV %d)" % (i+1)
        fsf_str += "\nset fmri(tempfilt_yn%d) %d\n" % ((i+1), fsf.TEMPFILT_YN[i])

        fsf_str += "\n# Add temporal derivative (EV %d)" % (i+1)
        fsf_str += "\nset fmri(deriv_yn%d) %d\n" % ((i+1), fsf.DERIV_YN[i])
        
        if fsf.SHAPE[i] == 0:
            fsf_str += "\n# Skip (EV %d)" % (i+1)
            fsf_str += "\nset fmri(skip%d) %d\n" % ((i+1), fsf.SKIP[i])

            fsf_str += "\n# Off (EV %d)" % (i+1)
            fsf_str += "\nset fmri(off%d) %d\n" % ((i+1), fsf.OFF[i])

            fsf_str += "\n# On (EV %d)" % (i+1)
            fsf_str += "\nset fmri(on%d) %d\n" % ((i+1), fsf.ON[i])

            fsf_str += "\n# Phase (EV %d)" % (i+1)
            fsf_str += "\nset fmri(phase%d) %d\n" % ((i+1), fsf.PHASE[i])

            fsf_str += "\n# Stop (EV %d)" % (i+1)
            fsf_str += "\nset fmri(stop%d) %d\n" % ((i+1), fsf.STOP[i])

        elif fsf.SHAPE[i] in [2, 3]:
            fsf_str += "\n# Custom EV file (EV %d)" % (i+1)
            fsf_str += "\nset fmri(custom%d) %s\n" % ((i+1), fsf.CUSTOM[i])

        if fsf.CONVOLVE[i] == 1:
            fsf_str += "\n# Gauss sigma (EV %d)" % (i+1)
            fsf_str += "\nset fmri(gausssigma%d) %1.2f\n" % ((i+1), fsf.GAUSSSIGMA[i])

            fsf_str += "\n# Gauss delay (EV %d)" % (i+1)
            fsf_str += "\nset fmri(gaussdelay%d) %1.2f\n" % ((i+1), fsf.GAUSSDELAY[i])
        elif fsf.CONVOLVE[i] == 2:
            fsf_str += "\n# Gamma sigma (EV %d)" % (i+1)
            fsf_str += "\nset fmri(gammasigma%d) %1.2f\n" % ((i+1), fsf.GAMMASIGMA[i])

            fsf_str += "\n# Gamma delay (EV %d)" % (i+1)
            fsf_str += "\nset fmri(gammadelay%d) %1.2f\n" % ((i+1), fsf.GAMMADELAY[i])

        for j in range(nev+1):
            fsf_str += "\n# Orthogonalise EV %d wrt EV %d" % ((i+1), j)
            fsf_str += "\nset fmri(ortho%d.%d) %d\n" % ((i+1), j, fsf.ORTHO[i][j])

        for j in range(fsf.MULTIPLE):
            fsf_str += "\n# Higher-level EV value for EV %d and input %d" % ((i+1), (j+1))
            fsf_str += "\nset fmri(evg%d.%d) %1.1f\n" % ((j+1), (i+1), fsf.EVG[i][j])

    for i in range(fsf.MULTIPLE):
        fsf_str += "\n# Group membership for input %d" % (i+1)
        fsf_str += "\nset fmri(groupmem.%d) %d\n" % ((i+1), fsf.GROUPMEM[i])

    fsf_str += "\n# Contrast & F-tests mode"
    fsf_str += "\n# real : control real EVs"
    fsf_str += "\n# orig : control original EVs"
    fsf_str += "\nset fmri(con_mode_old) %s" % fsf.CON_MODE_OLD
    fsf_str += "\nset fmri(con_mode) %s\n" % fsf.CON_MODE

    for i in range(fsf.NCON_REAL):
        fsf_str += "\n# Display images for contrast_%s %d" % ("real", (i+1))
        fsf_str += "\nset fmri(conpic_%s.%d) %d\n" % ("real", (i+1), fsf.CONPIC_REAL[i])

        fsf_str += "\n# Title for contrast_%s %d" % ("real", (i+1))
        fsf_str += "\nset fmri(conname_%s.%d) %s\n" % ("real", (i+1), fsf.CONNAME_REAL[i])

        for j in range(fsf.EVS_REAL):
            fsf_str += "\n# Real contrast_%s vector %d element %d" % ("real", (i+1), j+1)
            fsf_str += "\nset fmri(con_%s%d.%d) %d\n" % ("real", (i+1), j+1, fsf.CON_REAL[i][j])

    """for i in range(fsf.NCON_ORIG):
        fsf_str += "\n# Display images for contrast_%s %d" % ("orig", (i+1))
        fsf_str += "\nset fmri(conpic_%s.%d) %d\n" % ("orig", (i+1), fsf.CONPIC_ORIG[i])

        fsf_str += "\n# Title for contrast_%s %d" % ("orig", (i+1))
        fsf_str += "\nset fmri(conname_%s.%d) %s\n" % ("orig", (i+1), fsf.CONNAME_ORIG[i])

        for j in range(fsf.EVS_ORIG):
            fsf_str += "\n# Real contrast_%s vector %d element %d" % ("orig", (i+1), (j+1))
            fsf_str += "\nset fmri(con_%s%d.%d) %d\n" % ("orig", (i+1), (j+1), fsf.CON_ORIG[i][j])
"""
    fsf_str += "\n# Contrast masking - use >0 instead of thresholding?"
    fsf_str += "\nset fmri(conmask_zerothresh_yn) %d\n" % fsf.CONMASK_ZEROTHRESH_YN

    fsf_str += "\n# Do contrast masking at all?"
    fsf_str += "\nset fmri(conmask1_1) %d\n" % fsf.CONMASK1_1

    if fsf.VERSION >= 5.98:
        fsf_str += "\n##########################################################"
        fsf_str += "\n# Now options that don't appear in the GUI\n"
        #fsf_str += "\n# Alternative example_func image (not derived from input 4D dataset"
        #fsf_str += "\nset fmri(alternative_example_func) %s\n" % fsf.ALTERNATIVE_EXAMPLE_FUNC
        fsf_str += "\n# Alternative (to BETting) mask image"
        fsf_str += "\nset fmri(alternative_mask) %s\n" % fsf.ALTERNATIVE_MASK
        fsf_str += "\n# Initial structural space registration initialisation transform"
        fsf_str += "\nset fmri(init_initial_highres) %s\n" % fsf.INIT_INITIAL_HIGHRES
        fsf_str += "\n# Structural space registration initialisation transform"
        fsf_str += "\nset fmri(init_highres) %s\n" % fsf.INIT_HIGHRES
        fsf_str += "\n# Standard space registration initialisation transform"
        fsf_str += "\nset fmri(init_standard) %s\n" % fsf.INIT_STANDARD
        fsf_str += "\n# For full FEAT analysis: overwrite existing .feat output dir?"
        fsf_str += "\nset fmri(overwrite_yn) %d\n" % fsf.OVERWRITE_YN

    with open(argv[0], 'w') as fsffile:
        fsffile.write(fsf_str)

if __name__ == "__main__":
    main(sys.argv[1:])