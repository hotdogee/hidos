$(document).ready(function () {
  if ($('#result-list').length) { // check if user is logged in
    var running_template = $('#loading-template').html();
    var view_btn_compiled = _.template($('#viewer-btn-template').html());
    var cellq_name_compiled = _.template($('#cellq-name-template').html());
    var date_now = (new Date()).toLocaleDateString();
    var result_table;
    result_table = $('#result-list').DataTable({
      ajax: {
        'url': 'api/v1/tasks',
        'dataSrc': ''
      },
      deferRender: true,
      scroller: true,
      scrollY: 500,
      responsive: true,
      order: [[5, 'desc']],
      dom: 'Bfrtip',
      oLanguage:{
        "sSearch": "<span>Search File: </span>"
      },
      columns: [
        {
          name: 'viewer', data: 'url', width: '50px', orderable: false,
          render: function (data, type, row, meta) {
            if (type === 'display')
              return view_btn_compiled({
                task_url: data,
                result_img: row.result_img
              });
            else
              return data;
          }
        },
        {
          name: 'file-name', data: 'uploaded_filename',
          render: function (data, type, row, meta) {
            if (type === 'display')
                  return cellq_name_compiled({ name: data });
            else
              return data;
          }
        },
        {
          name: 'extremity', type: 'num', data: 'extremity', defaultContent: running_template, className: 'dt-center',
          render: function (data, type, row, meta) {
          console.log(type);
            if (row.status === 'running')
              return running_template;
            else if (row.status === 'failed')
              return row.status
            else
              return type === 'display' ? data  : data;
          }
        },
          {
          name: 'junction', type: 'num', data: 'junction', defaultContent: running_template, className: 'dt-center',
          render: function (data, type, row, meta) {
            if (row.status === 'running')
              return running_template;
            else if (row.status === 'failed')
              return row.status
            else
              return type === 'display' ? data  : data;
          }
        },
          {
          name: 'connectivity', type: 'num', data: 'connectivity', defaultContent: running_template, className: 'dt-center',
          render: function (data, type, row, meta) {
            if (row.status === 'running')
              return running_template;
            else if (row.status === 'failed')
              return row.status
            else
              return type === 'display' ? data  : data;
          }
        },          {
          name: 'total_network_length', type: 'num', data: 'total_network_length', defaultContent: running_template, className: 'dt-center',
          render: function (data, type, row, meta) {
            if (row.status === 'running')
              return running_template;
            else if (row.status === 'failed')
              return row.status
            else
              return type === 'display' ? data  : data;
          }
        },          {
          name: 'branch', type: 'num', data: 'branch', defaultContent: running_template, className: 'dt-center',
          render: function (data, type, row, meta) {
            if (row.status === 'running')
              return running_template;
            else if (row.status === 'failed')
              return row.status
            else
              return type === 'display' ? data  : data;
          }
        },          {
          name: 'total_branch_length', type: 'num', data: 'total_branch_length', defaultContent: running_template, className: 'dt-center',
          render: function (data, type, row, meta) {
            if (row.status === 'running')
              return running_template;
            else if (row.status === 'failed')
              return row.status
            else
              return type === 'display' ? data  : data;
          }
        },          {
          name: 'mean_branch_length', type: 'num', data: 'mean_branch_length', defaultContent: running_template, className: 'dt-center',
          render: function (data, type, row, meta) {
            if (row.status === 'running')
              return running_template;
            else if (row.status === 'failed')
              return row.status
            else
              return type === 'display' ? data  : data;
          }
        },          {
          name: 'std_branch_length', type: 'num', data: 'std_branch_length', defaultContent: running_template, className: 'dt-center',
          render: function (data, type, row, meta) {
            if (row.status === 'running')
              return running_template;
            else if (row.status === 'failed')
              return row.status
            else
              return type === 'display' ? data  : data;
          }
        },          {
          name: 'segment', type: 'num', data: 'segment', defaultContent: running_template, className: 'dt-center',
          render: function (data, type, row, meta) {
            if (row.status === 'running')
              return running_template;
            else if (row.status === 'failed')
              return row.status
            else
              return type === 'display' ? data  : data;
          }
        },          {
          name: 'total_segment_length', type: 'num', data: 'total_segment_length', defaultContent: running_template, className: 'dt-center',
          render: function (data, type, row, meta) {
            if (row.status === 'running')
              return running_template;
            else if (row.status === 'failed')
              return row.status
            else
              return type === 'display' ? data  : data;
          }
        },          {
          name: 'mean_segment_length', type: 'num', data: 'mean_segment_length', defaultContent: running_template, className: 'dt-center',
          render: function (data, type, row, meta) {
            if (row.status === 'running')
              return running_template;
            else if (row.status === 'failed')
              return row.status
            else
              return type === 'display' ? data  : data;
          }
        },          {
          name: 'std_segment_length', type: 'num', data: 'std_segment_length', defaultContent: running_template, className: 'dt-center',
          render: function (data, type, row, meta) {
            if (row.status === 'running')
              return running_template;
            else if (row.status === 'failed')
              return row.status
            else
              return type === 'display' ? data  : data;
          }
        },          {
          name: 'mesh', type: 'num', data: 'mesh', defaultContent: running_template, className: 'dt-center',
          render: function (data, type, row, meta) {
            if (row.status === 'running')
              return running_template;
            else if (row.status === 'failed')
              return row.status
            else
              return type === 'display' ? data  : data;
          }
        },          {
          name: 'total_mesh_area', type: 'num', data: 'total_mesh_area', defaultContent: running_template, className: 'dt-center',
          render: function (data, type, row, meta) {
            if (row.status === 'running')
              return running_template;
            else if (row.status === 'failed')
              return row.status
            else
              return type === 'display' ? data  : data;
          }
        },          {
          name: 'mean_mesh_area', type: 'num', data: 'mean_mesh_area', defaultContent: running_template, className: 'dt-center',
          render: function (data, type, row, meta) {
            if (row.status === 'running')
              return running_template;
            else if (row.status === 'failed')
              return row.status
            else
              return type === 'display' ? data  : data;
          }
        },          {
          name: 'std_mesh_area', type: 'num', data: 'std_mesh_area', defaultContent: running_template, className: 'dt-center',
          render: function (data, type, row, meta) {
            if (row.status === 'running')
              return running_template;
            else if (row.status === 'failed')
              return row.status
            else
              return type === 'display' ? data  : data;
          }
        },          {
          name: 'total_mesh_perimeter', type: 'num', data: 'total_mesh_perimeter', defaultContent: running_template, className: 'dt-center',
          render: function (data, type, row, meta) {
            if (row.status === 'running')
              return running_template;
            else if (row.status === 'failed')
              return row.status
            else
              return type === 'display' ? data  : data;
          }
        },         {
          name: 'mean_mesh_perimeter', type: 'num', data: 'mean_mesh_perimeter', defaultContent: running_template, className: 'dt-center',
          render: function (data, type, row, meta) {
            if (row.status === 'running')
              return running_template;
            else if (row.status === 'failed')
              return row.status
            else
              return type === 'display' ? data  : data;
          }
        },         {
          name: 'std_mesh_perimeter', type: 'num', data: 'std_mesh_perimeter', defaultContent: running_template, className: 'dt-center',
          render: function (data, type, row, meta) {
            if (row.status === 'running')
              return running_template;
            else if (row.status === 'failed')
              return row.status
            else
              return type === 'display' ? data  : data;
          }
        },
        {
          name: 'created', type: 'date', data: 'created',
          render: function (data, type, row, meta) {
            var date = (new Date(data));
            if (type === 'display') {
              var date_str = date.toLocaleDateString();
              if (date_now === date_str)
                return date.toLocaleTimeString();
              else
                return date_str;
            }
            else
              return date;
          }
        }
      ],
      createdRow: function (row, data, index) {
        // initialize bootstrap tooltip
        $('.viewer-btn', row);
      },
      buttons: [
        {
          extend: 'collection',
          text: '<i class="material-icons">cloud_download</i>',
          buttons: [
            {
              extend: 'copy',
              exportOptions: {
                columns: (idx, data, node) => idx !== 0
              }
            },
            {
              extend: 'csv',
              exportOptions: {
                columns: (idx, data, node) => idx !== 0
              }
            },
            {
              extend: 'excel',
              exportOptions: {
                columns: (idx, data, node) => idx !== 0
              }
            },
            {
              extend: 'pdf',
              exportOptions: {
                columns: (idx, data, node) => idx !== 0
              }
            },
          ]
        },
      ],
      columnDefs: [
            {
                "targets": [2,5,6,7,8,9,10,11,12,13,15,16,17,18,19,20],
                "visible": false,
            },
            {
                "searchable": false, "targets": [0,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
            },
        ]
    });
    var unfinished = ['queued', 'running'];
    var unfinished_task_ids;
    var polling = false;
    $('#result-list').on('xhr.dt', function (e, settings, json, xhr) {
      // json data loaded
      // get a list of queued and running tasks
      //console.log(e, settings, json, xhr);
      if (!json) return; // consecutive ajax.reload() may result in 'abort' status
      unfinished_task_ids = _.pluck(_.filter(json, (t) => _.contains(unfinished, t.status)), 'id');
      //console.log(unfinished_task_ids);
      if (unfinished_task_ids.length > 0 && polling == false) {
        polling = true;
        var finished = ['success', 'failed'];
        var poll = function () {
          $.ajax({
            url: 'api/v1/tasks/running',
            dataType: 'json',
            type: 'GET',
            traditional: true,
            success: function (data, status) {
              // console.log(_.some(finished, (c) => _.contains(_.pluck(data.data, 'result_status'), c)));
              if (data.length < unfinished_task_ids.length) {
                polling = false;
                result_table.ajax.reload();
              } else
                setTimeout(poll, 3000);
            }
          });
        };
        poll();
      } else {
        polling = false;
      }
    });


     // django csrf token set up
     // using jQuery
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    // Get the template HTML and remove it from the doumenthe template HTML and remove it from the doument
    var previewNode = document.querySelector("#dz-template");
    previewNode.id = "";
    var previewTemplate = previewNode.parentNode.innerHTML;
    previewNode.parentNode.removeChild(previewNode);

     var myDropzone = new Dropzone(document.querySelector(".mdl-layout__content"), {
        url: 'api/v1/tasks', // Set the url
        thumbnailWidth: 100,
        thumbnailHeight: 100,
        parallelUploads: 2,
        previewTemplate: previewTemplate,
        autoQueue: true, // Make sure the files aren't queued until manually added
        previewsContainer: "#dz-preview", // Define the container to display the previews
        clickable: ".dz-upload-button",
        sending:  function(file, xhr, formData) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        },
        init: function(){

           this.on("dragenter", function(event){
               document.querySelector(".mdl-layout__content").style.border= "3px solid #CDDC39";
            });
            this.on("dragover", function(event){
               document.querySelector(".mdl-layout__content").style.border= "3px solid #CDDC39";
            });
            this.on("dragleave", function(event){
               document.querySelector(".mdl-layout__content").style.border= "0px solid";
            });
            this.on("drop", function(event){
                document.querySelector(".mdl-layout__content").style.border= "0px solid";
            });

            this.on("success", function(file, responseText){
                result_table.ajax.reload();
                 file.previewElement.getElementsByClassName("dz-success-mark")[0].style.display = "block";
            });

            this.on("error", function(file, erroMessage, xhr){
                file.previewElement.getElementsByClassName("dz-error-mark")[0].style.display = "block";
            });

            this.on("uploadprogress", function(file, progress, bytesSent){
                console.log(file);
                file.previewElement.getElementsByClassName("mdl-progress")[0].addEventListener('mdl-componentupgraded', function() {
                    this.MaterialProgress.setProgress(progress);
                 });
            });
      }
     });
  } else {
    Dropzone.options.addPhotos = {
      maxFilesize: 256, // MB
      uploadMultiple: false,
      maxFiles: 1,
      thumbnailWidth: null,
      thumbnailHeight: 120,
      dictDefaultMessage: 'Drop image here to upload',
      init: function () {
        this.on('success', function (file, response) {
          //console.log(file, response);
          window.location = window.location + response.task_id;
        });
      }
    };
  }
});
