$(document).ready(function () {
  if ($('#result-list').length) { // check if user is logged in
    var running_template = '<i>Running ' + $('#loading-template').html() + '</i>';
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
      order: [[3, 'desc']],
      dom: 'Bfrtip',
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
          name: 'count', type: 'num', data: 'soma_count', defaultContent: running_template, width: '100px',
          render: function (data, type, row, meta) {
            if (!data)
              return running_template;
            else
              return type === 'display' ? data  : data;
          }
        },
        {
          name: 'created', type: 'date', data: 'created', width: '100px',
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
        $('.viewer-btn', row).tooltip();
      },
      buttons: [
        {
          extend: 'collection',
          text: '<span class="glyphicon glyphicon-cloud-download" aria-hidden="true"></span> Export',
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
              console.log(_.some(finished, (c) => _.contains(_.pluck(data.data, 'result_status'), c)));
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
    Dropzone.options.addPhotos = {
      maxFilesize: 256, // MB
      uploadMultiple: false,
      parallelUploads: 2,
      maxFiles: null,
      thumbnailWidth: null,
      thumbnailHeight: 120,
      dictDefaultMessage: 'Drop one or more images here to upload',
      init: function () {
        this.on('success', function (file, response) {
          // reload result table data
          result_table.ajax.reload()
        });
      }
    };
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
