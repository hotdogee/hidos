var Input_id = 0;
var Input_filename_array = [];
if (!String.prototype.format) {
    String.prototype.format = function() {
        var args = arguments;
        return this.replace(/{(\d+)}/g, function(match, number) { 
            return typeof args[number] != 'undefined'
                ? args[number]
                : match
            ;
        });
    };
}

function add_4D_data() {
    var data_filename = document.getElementById("4D_data").value;
    if (data_filename == ""){
        window.alert('Please select a file.');
        return;
    }
    else if(Input_filename_array.indexOf(data_filename) >= 0){
        window.alert("File " + data_filename + " has been selected.");
        return;
    }
    Input_filename_array.push(data_filename);
    var n = Input_filename_array.length;
    document.getElementById("nInputs").innerHTML = "Number of inputs: " + n.toString();
    
    refresh_data_list();
}

function remove_4D_data() {
    var n = Input_filename_array.length;
    for (i = 0; i < n; i++){
        var data = document.getElementById("4D_data_id" + i.toString());
        if (data.checked){
            var index = Input_filename_array.indexOf(data.value);
            if (index >= 0){
                Input_filename_array.splice(index, 1);
            }
        }
    }
    n = Input_filename_array.length;
    document.getElementById("nInputs").innerHTML = "Number of inputs: " + n.toString();
    refresh_data_list();
}

function refresh_data_list(){
    var data_list = document.getElementById("4D_data_list");
    data_list.innerHTML = '';
    for (i = 0; i < Input_filename_array.length; i++){
        var checkbox = document.createElement('input');
        checkbox.type = "checkbox";
        checkbox.name = "name";
        checkbox.value = Input_filename_array[i];
        checkbox.id = "4D_data_id" + i.toString();
        data_list.appendChild(checkbox);
        
        var label = document.createElement('label')
        label.htmlFor = "4D_data_id" + i.toString();
        label.appendChild(document.createTextNode(Input_filename_array[i]));
        data_list.appendChild(label);
        data_list.innerHTML += "<br>";
    }
}

function isNumber(evt) {
    evt = (evt) ? evt : window.event;
    var charCode = (evt.which) ? evt.which : evt.keyCode;
    if (charCode > 31 && (charCode < 48 || charCode > 57)) {
        return false;
    }
    return true;
}

function get_shapePanel(shape, id){
    var conv =  document.getElementById('conv'+id.toString()+'_p');
    if (shape === "0"){
        panel = '<label class="ev_p">Skip (s)</label>';
        panel += '<input type="text" value="0" class="ev_p" id="skip{0}">'.format(id);
        panel += '<br><label class="ev_p">Off (s)</label>';
        panel += '<input type="text" value="30" class="ev_p" id="off{0}">'.format(id);
        panel += '<br><label class="ev_p">On (s)</label>';
        panel += '<input type="text" value="30" class="ev_p" id="on{0}">'.format(id);
        panel += '<br><label class="ev_p">Phase (s)</label>';
        panel += '<input type="text" value="0" class="ev_p" id="phase{0}">'.format(id);
        panel += '<br><label class="ev_p">Stop after (s)</label>';
        panel += '<input type="text" value="-1" class="ev_p" id="stop{0}">'.format(id);        
        if (typeof(conv) != 'undefined' && conv != null){
            if (conv.style.visibility === 'hidden'){
                conv.style.visibility = 'visible';
                cv_p = document.getElementById('conv'+id.toString()+'_div');
                cv_p.innerHTML = get_convPanel(conv.value, id);
            }
        }
    } else if (shape === "1"){
        panel = '<label class="ev_p">Skip (s)</label>';
        panel += '<input type="text" value="0" class="ev_p" id="skip{0}">'.format(id);
        panel += '<br><label class="ev_p">Period (s)</label>';
        panel += '<input type="text" value="60" class="ev_p" id="period{0}">'.format(id);
        panel += '<br><label class="ev_p">Phase (s)</label>';
        panel += '<input type="text" value="-6" class="ev_p" id="phase{0}">'.format(id);
        panel += '<br><label class="ev_p">Harmonics</label>';
        panel += '<input type="text" value="0" class="ev_p" id="nharmonics{0}">'.format(id);
        panel += '<br><label class="ev_p">Stop after (s)</label>';
        panel += '<input type="text" value="-1" class="ev_p" id="stop{0}">'.format(id);
        if (typeof(conv) != 'undefined' && conv != null){
            if (conv.style.visibility = 'visible'){
                conv.style.visibility = 'hidden';
                cv_p = document.getElementById('conv'+id.toString()+'_div');
                cv_p.innerHTML = '';
            }
        }
    } else if (shape === "2" || shape === "3"){
        panel = '<label for="custom{0}">Filename</label>'.format(id);
        panel += '<input type="file" id="custom{0}">'.format(id);
        if (typeof(conv) != 'undefined' && conv != null){
            if (conv.style.visibility === 'hidden'){
                conv.style.visibility = 'visible';
                cv_p = document.getElementById('conv'+id.toString()+'_div');
                cv_p.innerHTML = get_convPanel(conv.value, id);
            }
        }
    } else if (shape === "9"){
        panel = '<label for="evs_vox_{0}">Filename</label>'.format(id);
        panel += '<input type="file" id="evs_vox_{0}">'.format(id);
        if (typeof(conv) != 'undefined' && conv != null){
            if (conv.style.visibility = 'visible'){
                conv.style.visibility = 'hidden';
                cv_p = document.getElementById('conv'+id.toString()+'_div');
                cv_p.innerHTML = '';
            }
        }
    } else if (shape === "10"){
        panel = '';
        if (typeof(conv) != 'undefined' && conv != null){
            if (conv.style.visibility = 'visible'){
                conv.style.visibility = 'hidden';
                cv_p = document.getElementById('conv'+id.toString()+'_div');
                cv_p.innerHTML = get_convPanel(conv.value, id);
            }
        }
    }
    
    return panel;
}

function refresh_shapePanel(e, id){
    sh_p = document.getElementById(e.id+'_div');
    sh_p.innerHTML = get_shapePanel(e.value, id);
}

function get_convPanel(conv, id){
    panel = '';
    if (conv === "0"){
        panel = '';
    } else if (conv === "1"){
        panel = '<label class="ev_p">Phase (s)</label>';
        panel += '<input type="text" value="0" class="ev_p" id="conv_phase{0}">'.format(id);
        panel += '<br><label class="ev_p">Sigma (s)</label>';
        panel += '<input type="text" value="2.8" class="ev_p" id="conv_sigma{0}">'.format(id);
        panel += '<br><label class="ev_p">Peak lag (s)</label>';
        panel += '<input type="text" value="5" class="ev_p" id="conv_delay{0}">'.format(id);
    } else if (conv === "2"){
        panel = '<label class="ev_p">Phase (s)</label>';
        panel += '<input type="text" value="0" class="ev_p" id="conv_phase{0}">'.format(id);
        panel += '<br><label class="ev_p">Stddev (s)</label>';
        panel += '<input type="text" value="3" class="ev_p" id="conv_stddev{0}">'.format(id);
        panel += '<br><label class="ev_p">Mean lag (s)</label>';
        panel += '<input type="text" value="6" class="ev_p" id="conv_delay{0}">'.format(id);
    } else if (conv === "3"){
        panel = '<label class="ev_p">Phase (s)</label>';
        panel += '<input type="text" value="0" class="ev_p" id="conv_phase{0}">'.format(id);
    } else if (conv === "4" || conv === "5" || conv === "6"){
        panel = '<label class="ev_p">Phase (s)</label>';
        panel += '<input type="text" value="0" class="ev_p" id="conv_phase{0}">'.format(id);
        panel += '<br><label class="ev_p">Number</label>';
        panel += '<input type="text" value="3" class="ev_p" id="conv_number{0}">'.format(id);
        panel += '<br><label class="ev_p">Windows (s)</label>';
        panel += '<input type="text" value="15" class="ev_p" id="conv_window{0}">'.format(id);
    } else {
        panel = '<label class="ev_p">Phase (s)</label>';
        panel += '<input type="text" value="0" class="ev_p" id="conv_phase{0}">'.format(id);
        panel += '<br><label for="conv_custom{0}">Filename</label>'.format(id);
        panel += '<input type="file" id="conv_custom{0}">'.format(id);
    }
    
    return panel;
}

function refresh_convPanel(e, id){
    cv_p = document.getElementById(e.id+'_div');
    cv_p.innerHTML = get_convPanel(e.value, id);
}

function fund_EVPanel(id){
    panel = '<p>EV name: <input type="text" value="" id="EVName{0}"></p>'.format(id);
    
    panel += '<p>Basic shape: ';
    panel += '<select id="shape{0}" onchange="refresh_shapePanel(this, {1})">'.format(id, id);
    panel += '<option value="10">Empty (all zeros)</option>';
    panel += '<option value="0">Square</option>';
    panel += '<option value="1">Sinusoid</option>';
    panel += '<option value="2">Custom (1 entry per volume)</option>';
    panel += '<option value="3" selected="selected">Custom (3 column format)</option>';
    panel += '<option value="9">Voxelwise</option></select></p>';
    
    panel += '<div id="shape{0}_div">'.format(id);
    panel += get_shapePanel("3", id);
    panel += '</div><br>';
    
    panel += '<p id="conv{0}_p">Convolution: '.format(id);
    panel += '<select id="conv{0}" onchange="refresh_convPanel(this)">'.format(id);
    panel += '<option value="0">None</option>';
    panel += '<option value="1">Gaussian</option>';
    panel += '<option value="2">Gamma</option>';
    panel += '<option value="3" selected="selected">Double-Gamma HRF</option>';
    //panel += '<option value="7">Optimal/custom basis functions</option>';
    panel += '<option value="4">Gamma basis functions</option>';
    panel += '<option value="5">Sine basis functions</option>';
    panel += '<option value="6">FIR basis functions</option></select></p>';

    panel += '<div id="conv{0}_div">'.format(id);
    panel += get_convPanel("3", id);
    panel += '</div>';
    
    return panel;
}



function fund_tabs(container, n, multi){
    var tab_header = '<ul class="nav nav-tabs">{0}</ul>';
    var tab_act = '<li class="active">{0}</li>';
    var tab = '<li>{0}</li>';
    var tab_menu = '<a data-toggle="tab" href="#{0}">{1}</a>';
    var tab_content = '<div class="tab-content">{0}</div>';
    var tab_item_act = '<div id="{0}" class="tab-pane fade in active">{1}</div>';
    var tab_item = '<div id="{0}" class="tab-pane fade">{1}</div>'
    if (multi){
        var header = tab_act.format(tab_menu.format('EV1', 'EV1'));
    } else {
        var header = tab_act.format(tab_menu.format('EVs', 'EVs'));
    }
    for (i = 1; i < n; i++){
        header += tab.format(tab_menu.format('EV'+(i+1).toString(), 'EV'+(i+1).toString()));
    }
    header = tab_header.format(header);
    
    if (multi){
        var content = tab_item_act.format('EV1', fund_EVPanel(1));
    } else {
        var content = tab_item_act.format('EVs', fund_EVPanel(1));
    }
    for (i = 1; i < n; i++){
        content += tab_item.format('EV'+(i+1).toString(), fund_EVPanel(i+1));
    }
    content = tab_content.format(content);
    
    container.innerHTML = header + content;
}


function refresh_evs_tabs(){
    var evs_tabs = document.getElementById("EVs_tabs_container");
    var same_tag = document.getElementById("evs_same_select");
    var nEVs = document.getElementById("nEVs");
    if (nEVs.value === ""){
        window.alert("Please enter the number of events");
        return;
    }
    if (same_tag.value === "same"){
        fund_tabs(evs_tabs, 1, false);
        same_tag.disabled = true;
        nEVs.disabled = true;
    } else if (same_tag.value === "distinct"){
        var n = parseInt(nEVs.value, 10);
        fund_tabs(evs_tabs, n, true);
        same_tag.disabled = true;
        nEVs.disabled = true;
    }
    
}

function reset_evs(){
    document.getElementById("EVs_tabs_container").innerHTML = '';
    document.getElementById("evs_same_select").disabled = false;
    document.getElementById("nEVs").disabled = false;
    
    document.getElementById("Contrasts_container").innerHTML = '';
    document.getElementById("nCon").disabled = false;
}

function fund_cons(container){
    var table = '<table id="Con_table">{0}</table>';
    var table_title = '<tr><th></th><th>Title</th>{0}</tr>';
    var table_content = '<tr><td>OC{0}</td><td><input type="text" /></td>{1}</tr>';
    
    var nEVs = document.getElementById("nEVs");
    var nCon = document.getElementById("nCon");
    
    var m = parseInt(nEVs.value, 10);
    var n = parseInt(nCon.value, 10);
    
    var title = "";
    for (var j = 0; j < m; j++){
        title = title + '<th>EV' + (j+1).toString() + '</th>';
    }
    title = table_title.format(title);
    
    var content = "";
    for (var i = 0; i < n; i++){
        var tmp = "";
        for (var j = 0; j < m; j++){
            tmp = tmp + '<td><input type="text" style="width:30px" value="0" /></td>';
        }
        content = content + table_content.format(i+1, tmp);
    }
    container.innerHTML = table.format(title+content);
}

function refresh_contrasts(){
    var nCon = document.getElementById("nCon");
    var Con = document.getElementById("Contrasts_container");

    if (nCon.value === ""){
        window.alert("Please enter the number of contrasts");
        return;
    }
    fund_cons(Con);
    nCon.disabled = true;
}

function reset_contrasts(){
    document.getElementById("Contrasts_container").innerHTML = '';
    document.getElementById("nCon").disabled = false;
}

var npts = 24;
function show(){
    var nev = parseInt(document.getElementById("nEVs").value, 10);
    var ncon = parseInt(document.getElementById("nCon").value, 10);
    var fsf_str = '';
    var outpath = "/path/to/output"
    var standard = "/usr/local/fsl/data/standard/MNI152_T1_2mm_brain";
    
    fsf_str += '\n# FEAT version number';
    fsf_str += '\nset fmri(version) 6.00\n';
    
    fsf_str += '\n# Are we in MELODIC?';
    fsf_str += '\nset fmri(inmelodic) 0\n';

    fsf_str += '\n# Analysis level';
    fsf_str += '\n# 1 : First-level analysis';
    fsf_str += '\n# 2 : Higher-level analysis';
    fsf_str += '\nset fmri(level) 1\n';

    fsf_str += '\n# Which stages to run';
    fsf_str += '\n# 0 : No first-level analysis (registration and/or group stats only)';
    fsf_str += '\n# 7 : Full first-level analysis';
    fsf_str += '\n# 1 : Pre-processing';
    fsf_str += '\n# 2 : Statistics';
    fsf_str += '\nset fmri(analysis) 7\n';

    fsf_str += '\n# Use relative filenames';
    fsf_str += '\nset fmri(relative_yn) 0\n';

    fsf_str += '\n# Balloon help';
    fsf_str += '\nset fmri(help_yn) 0\n';

    fsf_str += '\n# Run Featwatcher';
    fsf_str += '\nset fmri(featwatcher_yn) 0\n';
    
    fsf_str += '\n# Cleanup first-level standard-space images';
    fsf_str += '\nset fmri(sscleanup_yn) 0\n';
    
    fsf_str += '\n# Output directory';
    fsf_str += '\nset fmri(outputdir) "{0}"\n'.format(outpath);
    
    fsf_str += '\n# TR(s)';
    fsf_str += '\nset fmri(tr) 3.0\n';
    
    fsf_str += '\n# Total volumes';
    fsf_str += '\nset fmri(npts) {0}\n'.format(npts);
    
    fsf_str += '\n# Delete volumes';
    fsf_str += '\nset fmri(ndelete) 0\n';
    
    fsf_str += '\n# Perfusion tag/control order';
    fsf_str += '\nset fmri(tagfirst) 1\n';

    fsf_str += '\n# Number of first-level analyses';
    fsf_str += '\nset fmri(multiple) {0}\n'.format(Input_filename_array.length);
    
    fsf_str += '\n# Higher-level input type';
    fsf_str += '\n# 1 : Inputs are lower-level FEAT directories';
    fsf_str += '\n# 2 : Inputs are cope images from FEAT directories';
    fsf_str += '\nset fmri(inputtype) 2\n';
    
    fsf_str += '\n# Carry out pre-stats processing?';
    fsf_str += '\nset fmri(filtering_yn) 1\n';
    
    fsf_str += '\n# Brain/background threshold, %';
    fsf_str += '\nset fmri(brain_thresh) 10\n';
    
    fsf_str += '\n# Critical z for design efficiency calculation';
    fsf_str += '\nset fmri(critical_z) 5.3\n';
    
    fsf_str += '\n# Noise level';
    fsf_str += '\nset fmri(noise) 0.66\n';
        
    fsf_str += '\n# Noise AR(1)';
    fsf_str += '\nset fmri(noisear) 0.34\n';
    
    fsf_str += '\n# Motion correction';
    fsf_str += '\n# 0 : None';
    fsf_str += '\n# 1 : MCFLIRT';
    fsf_str += '\nset fmri(mc) 1\n';
    
    fsf_str += '\n# Spin-history (currently obsolete)';
    fsf_str += '\nset fmri(sh_yn) 0\n';
    
    fsf_str += '\n# B0 fieldmap unwarping?';
    fsf_str += '\nset fmri(regunwarp_yn) 0\n';
    
    fsf_str += '\n# EPI dwell time (ms)';
    fsf_str += '\nset fmri(dwell) 0.7\n';
    
    fsf_str += '\n# EPI TE (ms)';
    fsf_str += '\nset fmri(te) 35\n';
    
    fsf_str += '\n# % Signal loss threshold';
    fsf_str += '\nset fmri(signallossthresh) 10\n';
    
    fsf_str += '\n# Unwarp direction';
    fsf_str += '\nset fmri(unwarp_dir) y-\n';

    fsf_str += '\n# Slice timing correction';
    fsf_str += '\n# 0 : None';
    fsf_str += '\n# 1 : Regular up (0, 1, 2, 3, ...)';
    fsf_str += '\n# 2 : Regular down';
    fsf_str += '\n# 3 : Use slice order file';
    fsf_str += '\n# 4 : Use slice timings file';
    fsf_str += '\n# 5 : Interleaved (0, 2, 4 ... 1, 3, 5 ... )';
    fsf_str += '\nset fmri(st) 0\n';
    
    fsf_str += '\n# Slice timings file';
    fsf_str += '\nset fmri(st_file) ""\n';
    
    fsf_str += '\n# BET brain extraction';
    fsf_str += '\nset fmri(bet_yn) 1\n';
    
    fsf_str += '\n# Spatial smoothing FWHM (mm)';
    fsf_str += '\nset fmri(smooth) 5\n';
    
    fsf_str += '\n# Intensity normalization';
    fsf_str += '\nset fmri(norm_yn) 0\n';
    
    fsf_str += '\n# Perfusion subtraction';
    fsf_str += '\nset fmri(perfsub_yn) 0\n';
    
    fsf_str += '\n# Highpass temporal filtering';
    fsf_str += '\nset fmri(temphp_yn) 0\n';
    
    fsf_str += '\n# Lowpass temporal filtering';
    fsf_str += '\nset fmri(templp_yn) 0\n';
    
    fsf_str += '\n# MELODIC ICA data exploration';
    fsf_str += '\nset fmri(melodic_yn) 0\n';
    
    fsf_str += '\n# Carry out main stats?';
    fsf_str += '\nset fmri(stats_yn) 1\n';
    
    fsf_str += '\n# Carry out prewhitening?';
    fsf_str += '\nset fmri(prewhiten_yn) 1\n';
    
    fsf_str += '\n# Add motion parameters to model';
    fsf_str += '\n# 0 : No';
    fsf_str += '\n# 1 : Yes';
    fsf_str += '\nset fmri(motionevs) 0';
    fsf_str += '\nset fmri(motionevsbeta) ""';
    fsf_str += '\nset fmri(scriptevsbeta) ""\n';
    
    fsf_str += '\n# Robust outlier detection in FLAME?';
    fsf_str += '\nset fmri(robust_yn) 0\n';
    
    fsf_str += '\n# Higher-level modelling';
    fsf_str += '\n# 3 : Fixed effects';
    fsf_str += '\n# 0 : Mixed Effects: Simple OLS';
    fsf_str += '\n# 2 : Mixed Effects: FLAME 1';
    fsf_str += '\n# 1 : Mixed Effects: FLAME 1+2';
    fsf_str += '\nset fmri(mixed_yn) 1\n';

    fsf_str += '\n# Number of EVs';
    fsf_str += '\nset fmri(evs_orig) {0}'.format(nev);
    fsf_str += '\nset fmri(evs_real) {0}'.format(nev*2);
    fsf_str += '\nset fmri(evs_vox) 0\n';
    
    fsf_str += '\n# Number of contrasts';
    fsf_str += '\nset fmri(ncon_orig) {0}'.format(ncon);
    fsf_str += '\nset fmri(ncon_real) {0}\n'.format(ncon);
    
    fsf_str += '\n# Number of F-tests';
    fsf_str += '\nset fmri(nftests_orig) 0';
    fsf_str += '\nset fmri(nftests_real) 0\n';
    
    fsf_str += '\n# Add constant column to design matrix? (obsolete)';
    fsf_str += '\nset fmri(constcol) 0\n';
    
    fsf_str += '\n# Carry out post-stats steps?';
    fsf_str += '\nset fmri(poststats_yn) 1\n';
    
    fsf_str += '\n# Pre-threshold masking?';
    fsf_str += '\nset fmri(threshmask) ""\n';
    
    fsf_str += '\n# Thresholding';
    fsf_str += '\n# 0 : None';
    fsf_str += '\n# 1 : Uncorrected';
    fsf_str += '\n# 2 : Voxel';
    fsf_str += '\n# 3 : Cluster';
    fsf_str += '\nset fmri(thresh) 0\n';
    
    fsf_str += '\n# P threshold';
    fsf_str += '\nset fmri(prob_thresh) 0.05\n';

    fsf_str += '\n# Z threshold';
    fsf_str += '\nset fmri(z_thresh) 2.3\n';

    fsf_str += '\n# Z min/max for colour rendering';
    fsf_str += '\n# 0 : Use actual Z min/max';
    fsf_str += '\n# 1 : Use preset Z min/max';
    fsf_str += '\nset fmri(zdisplay) 0\n';

    fsf_str += '\n# Z min in colour rendering';
    fsf_str += '\nset fmri(zmin) 2\n';

    fsf_str += '\n# Z max in colour rendering';
    fsf_str += '\nset fmri(zmax) 8\n';
    
    fsf_str += '\n# Colour rendering type';
    fsf_str += '\n# 0 : Solid blobs';
    fsf_str += '\n# 1 : Transparent blobs';
    fsf_str += '\nset fmri(rendertype) 1\n';
    
    fsf_str += '\n# Background image for higher-level stats overlays';
    fsf_str += '\n# 1 : Mean highres';
    fsf_str += '\n# 2 : First highres';
    fsf_str += '\n# 3 : Mean functional';
    fsf_str += '\n# 4 : First functional';
    fsf_str += '\n# 5 : Standard space template';
    fsf_str += '\nset fmri(bgimage) 1\n';
    
    fsf_str += '\n# Create time series plots';
    fsf_str += '\nset fmri(tsplot_yn) 1\n';
    
    fsf_str += '\n# Registration to initial structural';
    fsf_str += '\nset fmri(reginitial_highres_yn) 0\n';

    fsf_str += '\n# Search space for registration to initial structural';
    fsf_str += '\n# 0   : No search';
    fsf_str += '\n# 90  : Normal search';
    fsf_str += '\n# 180 : Full search';
    fsf_str += '\nset fmri(reginitial_highres_search) 90\n';

    fsf_str += '\n# Degrees of Freedom for registration to initial structural';
    fsf_str += '\nset fmri(reginitial_highres_dof) 3\n';
    
    fsf_str += '\n# Registration to main structural';
    fsf_str += '\nset fmri(reghighres_yn) 1\n';
    
    fsf_str += '\n# Search space for registration to main structural';
    fsf_str += '\n# 0   : No search';
    fsf_str += '\n# 90  : Normal search';
    fsf_str += '\n# 180 : Full search';
    fsf_str += '\nset fmri(reghighres_search) 90\n';//.format(document.getElementById("linear_select1").value);
    
    fsf_str += '\n# Degrees of Freedom for registration to main structural';
    fsf_str += '\nset fmri(reghighres_dof) BBR\n';//.format(document.getElementById("dof_select1").value);
    
    fsf_str += '\n# Registration to standard image?';
    fsf_str += '\nset fmri(regstandard_yn) 1\n';
    
    fsf_str += '\n# Use alternate reference images?';
    fsf_str += '\nset fmri(alternateReference_yn) 0\n';
    
    fsf_str += '\n# Standard image';
    fsf_str += '\nset fmri(regstandard) "{0}"\n'.format(standard);
    
    fsf_str += '\n# Search space for registration to standard space';
    fsf_str += '\n# 0   : No search';
    fsf_str += '\n# 90  : Normal search';
    fsf_str += '\n# 180 : Full search';
    fsf_str += '\nset fmri(regstandard_search) 90\n';
    
    fsf_str += '\n# Degrees of Freedom for registration to standard space';
    fsf_str += '\nset fmri(regstandard_dof) 12\n';
    
    fsf_str += '\n# Do nonlinear registration from structural to standard space?';
    fsf_str += '\nset fmri(regstandard_nonlinear_yn) 1\n';
    
    fsf_str += '\n# Control nonlinear warp field resolution';
    fsf_str += '\nset fmri(regstandard_nonlinear_warpres) 10 \n';
    
    fsf_str += '\n# High pass filter cutoff';
    fsf_str += '\nset fmri(paradigm_hp) 100\n';
    
    fsf_str += '\n# Number of lower-level copes feeding into higher-level analysis';
    fsf_str += '\nset fmri(ncopeinputs) 0\n';
    
    for (var i = 0; i < Input_filename_array.length; i++){
        fsf_str += '\n# 4D AVW data or FEAT directory ({0})'.format(i+1);
        fsf_str += '\nset feat_files({0}) "{1}"\n'.format(i+1, Input_filename_array[i]);
    }
    
    fsf_str += '\n# Add confound EVs text file';
    fsf_str += '\nset fmri(confoundevs) 0\n';

    for (var i = 0; i < Input_filename_array.length; i++){
        fsf_str += "\n# Subject's structural image for analysis {0}".format(i+1);
        fsf_str += '\nset highres_files({0}) "{1}"\n'.format(i+1, document.getElementById("struct_data").value);
    }
    
    for (var i = 0; i < nev; i++){
        var same_tag = document.getElementById("evs_same_select");
        var n;
        if(same_tag.value === "same"){
            n = 1;
        } else {
            n = i+1;
        }
        var name = document.getElementById("EVName"+n.toString());
        var shape = document.getElementById("shape"+n.toString());
        
        fsf_str += '\n# EV {0} title'.format(i+1);
        fsf_str += '\nset fmri(evtitle{0}) "{1}"\n'.format(i+1, name.value);
        
        fsf_str += '\n# Basic waveform shape (EV {0})'.format(i+1);
        fsf_str += '\n# 0 : Square';
        fsf_str += '\n# 1 : Sinusoid';
        fsf_str += '\n# 2 : Custom (1 entry per volume)';
        fsf_str += '\n# 3 : Custom (3 column format)';
        fsf_str += '\n# 4 : Interaction';
        fsf_str += '\n# 10 : Empty (all zeros)';
        fsf_str += '\nset fmri(shape{0}) {1}\n'.format(i+1, shape.value);
        
        fsf_str += '\n# Convolution (EV {0})'.format(i+1);
        fsf_str += '\n# 0 : None';
        fsf_str += '\n# 1 : Gaussian';
        fsf_str += '\n# 2 : Gamma';
        fsf_str += '\n# 3 : Double-Gamma HRF';
        fsf_str += '\n# 4 : Gamma basis functions';
        fsf_str += '\n# 5 : Sine basis functions';
        fsf_str += '\n# 6 : FIR basis functions';
        
        if (shape.value === "0" || shape.value === "2" || shape.value === "3"){
            var conv = document.getElementById("conv"+n.toString());
            var conv_phase = document.getElementById("conv_phase"+n.toString());
            fsf_str += '\nset fmri(convolve{0}) {1}\n'.format(i+1, conv.value);
        
            fsf_str += '\n# Convolve phase (EV {0})'.format(i+1);
            fsf_str += '\nset fmri(convolve_phase{0}) {1}\n'.format(i+1, conv_phase.value);
        } else {
            fsf_str += '\nset fmri(convolve{0}) {1}\n'.format(i+1, 0);
        
            fsf_str += '\n# Convolve phase (EV {0})'.format(i+1);
            fsf_str += '\nset fmri(convolve_phase{0}) {1}\n'.format(i+1, 0);
        }
        
        fsf_str += '\n# Apply temporal filtering (EV {0})'.format(i+1);
        fsf_str += '\nset fmri(tempfilt_yn{0}) {1}\n'.format(i+1, 1);
        
        fsf_str += '\n# Add temporal derivative (EV {0})'.format(i+1);
        fsf_str += '\nset fmri(deriv_yn{0}) {1}\n'.format(i+1, 1);
        
        if (shape.value === "0"){
            var skip = document.getElementById("skip"+n.toString());
            var off = document.getElementById("off"+n.toString());
            var on = document.getElementById("on"+n.toString());
            var phase = document.getElementById("phase"+n.toString());
            var stop = document.getElementById("stop"+n.toString());
            fsf_str += '\n# Skip (EV {0})'.format(i+1);
            fsf_str += '\nset fmri(skip{0}) {1}\n'.format(i+1, skip.value);

            fsf_str += '\n# Off (EV {0})'.format(i+1);
            fsf_str += '\nset fmri(off{0}) {1}\n'.format(i+1, off.value);

            fsf_str += '\n# On (EV {0})'.format(i+1);
            fsf_str += '\nset fmri(on{0}) {1}\n'.format(i+1, on.value);

            fsf_str += '\n# Phase (EV {0})'.format(i+1);
            fsf_str += '\nset fmri(phase{0}) {1}\n'.format(i+1, phase.value);

            fsf_str += '\n# Stop (EV {0})'.format(i+1);
            fsf_str += '\nset fmri(stop{0}) {1}\n'.format(i+1, stop.value);
        } else if (shape.value === "1"){
            var skip = document.getElementById("skip"+n.toString());
            var period = document.getElementById("period"+n.toString());
            var phase = document.getElementById("phase"+n.toString());
            var nharmonics = document.getElementById("nharmonics"+n.toString());
            var stop = document.getElementById("stop"+n.toString());
            fsf_str += '\n# Skip (EV {0})'.format(i+1);
            fsf_str += '\nset fmri(skip{0}) {1}\n'.format(i+1, skip.value);
            
            fsf_str += '\n# Period (EV {0})'.format(i+1);
            fsf_str += '\nset fmri(period{0}) {1}\n'.format(i+1, period.value);
            
            fsf_str += '\n# Phase (EV {0})'.format(i+1);
            
            fsf_str += '\n# Sinusoid harmonics (EV {0})'.format(i+1);
            fsf_str += '\nset fmri(nharmonics{0}) {1}\n'.format(i+1, nharmonics.value);
            
            fsf_str += '\n# Stop (EV {0})'.format(i+1);
            fsf_str += '\nset fmri(stop{0}) {1}\n'.format(i+1, stop.value);
        } else if (shape.value === "2" || shape.value === "3"){
            var custom = document.getElementById("custom"+n.toString());
            fsf_str += '\n# Custom EV file (EV {0})'.format(i+1);
            fsf_str += '\nset fmri(custom{0}) "{1}"\n'.format(i+1, custom.value);
        } else if (shape.value === "9"){
            var evs_vox_ = document.getElementById("evs_vox_"+n.toString());
            fsf_str += '\n# EV {0} voxelwise image filename'.format(i+1);
            fsf_str += '\nset fmri(evs_vox_{0}) {1}\n'.format(i+1, evs_vox_.value);
        }
        
        if (shape.value === "0" || shape.value === "2" || shape.value === "3"){
            if (conv.value === "1"){
                var conv_sigma = document.getElementById("conv_sigma"+n.toString());
                var conv_delay = document.getElementById("conv_delay"+n.toString());
                fsf_str += '\n# Gauss sigma (EV {0})'.format(i+1);
                fsf_str += '\nset fmri(gausssigma{0}) {1}\n'.format(i+1, conv_sigma.value);
                
                fsf_str += '\n# Gauss delay (EV {0})'.format(i+1);
                fsf_str += '\nset fmri(gaussdelay{0}) {1}\n'.format(i+1, conv_delay.value);
            } else if (conv.value === "2"){
                var conv_stddev = document.getElementById("conv_stddev"+n.toString());
                var conv_delay = document.getElementById("conv_delay"+n.toString());
                fsf_str += '\n# Gamma sigma (EV {0})'.format(i+1);
                fsf_str += '\nset fmri(gammasigma{0}) {1}\n'.format(i+1, conv_stddev.value);
                
                fsf_str += '\n# Gauss delay (EV {0})'.format(i+1);
                fsf_str += '\nset fmri(gaussdelay{0}) {1}\n'.format(i+1, conv_delay.value);
            } else if (conv.value === "4"){
                var conv_number = document.getElementById("conv_number"+n.toString());
                var conv_window = document.getElementById("conv_window"+n.toString());
                fsf_str += '\n# Gamma basis functions number (EV {0})'.format(i+1);
                fsf_str += '\nset fmri(basisfnum{0}) {1}\n'.format(i+1, conv_number.value);
                
                fsf_str += '\n# Gamma basis functions window(s) (EV {0})'.format(i+1);
                fsf_str += '\nset fmri(basisfwidth{0}) {1}\n'.format(i+1, conv_window.value);
                
                fsf_str += '\n# Orth basis functions wrt each other';
                fsf_str += '\nset fmri(basisorth{0}) 0\n'.format(i+1);
            } else if (conv.value === "5"){
                var conv_number = document.getElementById("conv_number"+n.toString());
                var conv_window = document.getElementById("conv_window"+n.toString());
                fsf_str += '\n# Sine basis functions number (EV {0})'.format(i+1);
                fsf_str += '\nset fmri(basisfnum{0}) {1}\n'.format(i+1, conv_number.value);
                
                fsf_str += '\n# Sine basis functions window(s) (EV {0})'.format(i+1);
                fsf_str += '\nset fmri(basisfwidth{0}) {1}\n'.format(i+1, conv_window.value);
                
                fsf_str += '\n# Orth basis functions wrt each other';
                fsf_str += '\nset fmri(basisorth{0}) 0\n'.format(i+1);
            } else if (conv.value === "6"){
                var conv_number = document.getElementById("conv_number"+n.toString());
                var conv_window = document.getElementById("conv_window"+n.toString());
                fsf_str += '\n# FIR basis functions number (EV {0})'.format(i+1);
                fsf_str += '\nset fmri(basisfnum{0}) {1}\n'.format(i+1, conv_number.value);
                
                fsf_str += '\n# FIR basis functions window(s) (EV {0})'.format(i+1);
                fsf_str += '\nset fmri(basisfwidth{0}) {1}\n'.format(i+1, conv_window.value);
                
                fsf_str += '\n# Orth basis functions wrt each other';
                fsf_str += '\nset fmri(basisorth{0}) 0\n'.format(i+1);
            } else if (conv.value === "7"){
            }
        }
        
        for (var j = 0; j <= nev; j++){
            fsf_str += '\n# Orthogonalise EV {0} wrt EV {1}'.format(i+1, j);
            fsf_str += '\nset fmri(ortho{0}.{1}) 0\n'.format(i+1, j);
        }
    }
    fsf_str += '\n# Contrast & F-tests mode';
    fsf_str += '\n# real : control real EVs';
    fsf_str += '\n# orig : control original EVs';
    fsf_str += '\nset fmri(con_mode_old) {0}'.format("orig");
    fsf_str += '\nset fmri(con_mode) {0}\n'.format("orig");
    
    var table = document.getElementById("Con_table");
    for (var i = 0; i < ncon; i++){
        fsf_str += '\n# Display images for contrast_real {0}'.format(i+1);
        fsf_str += '\nset fmri(conpic_real.{0}) 1\n'.format(i+1);
    
        fsf_str += '\n# Title for contrast_real {0}'.format(i+1);
        fsf_str += '\nset fmri(conname_real.{0}) "{1}"\n'.format(i+1, table.rows[i+1].cells[1].firstChild.value);
    
        for (var j = 0; j < nev*2; j++){
            fsf_str += '\n# Real contrast_real vector {0} element {1}'.format(i+1, j+1);
            if (j % 2 === 0){
                fsf_str += '\nset fmri(con_real{0}.{1}) {2}\n'.format(i+1, j+1, table.rows[i+1].cells[j/2+2].firstChild.value);
            } else {
                fsf_str += '\nset fmri(con_real{0}.{1}) 0\n'.format(i+1, j+1);
            }
        }
    }
    
    for (var i = 0; i < ncon; i++){
        fsf_str += '\n# Display images for contrast_orig {0}'.format(i+1);
        fsf_str += '\nset fmri(conpic_orig.{0}) 1\n'.format(i+1);
    
        fsf_str += '\n# Title for contrast_orig {0}'.format(i+1);
        fsf_str += '\nset fmri(conname_orig.{0}) "{1}"\n'.format(i+1, table.rows[i+1].cells[1].firstChild.value);
    
        for (j = 0; j < nev; j++){
            fsf_str += '\n# Real contrast_orig vector {0} element {1}'.format(i+1, j+1);
            fsf_str += '\nset fmri(con_orig{0}.{1}) {2}\n'.format(i+1, j+1, table.rows[i+1].cells[j+2].firstChild.value);
        }
    }
    
    fsf_str += '\n# Contrast masking - use >0 instead of thresholding?';
    fsf_str += '\nset fmri(conmask_zerothresh_yn) 0\n';
    
    for (var i = 0; i < ncon; i++){
        for (var j = 0; j < ncon; j++){
            if (i === j){
                continue;
            }
            fsf_str += '\n# Mask real contrast/F-test {0} with real contrast/F-test {1}?'.format(i+1, j+1);
            fsf_str += '\nset fmri(conmask{0}_{1}) 0\n'.format(i+1, j+1);
        }
    }
    
    fsf_str += '\n# Do contrast masking at all?';
    fsf_str += '\nset fmri(conmask1_1) 0\n';
    
    fsf_str += '\n##########################################################';
    fsf_str += "\n# Now options that don't appear in the GUI\n";
    
    fsf_str += '\n# Alternative (to BETting) mask image';
    fsf_str += '\nset fmri(alternative_mask) ""\n';
    
    fsf_str += '\n# Initial structural space registration initialisation transform';
    fsf_str += '\nset fmri(init_initial_highres) ""\n';
    
    fsf_str += '\n# Structural space registration initialisation transform';
    fsf_str += '\nset fmri(init_highres) ""\n';
    
    fsf_str += '\n# Standard space registration initialisation transform';
    fsf_str += '\nset fmri(init_standard) ""\n';
    
    fsf_str += '\n# For full FEAT analysis: overwrite existing .feat output dir?';
    fsf_str += '\nset fmri(overwrite_yn) 0\n';
    
    document.getElementById("show").innerHTML=fsf_str;
    //document.getElementById("show").innerHTML=fsf_str.replace(/\n/g,'<br>');
    
}

function copy_to_clipboard(event){
    var textarea = document.getElementById("show");
    textarea.select();
    document.execCommand('copy');
}

function go(){
    show();
}