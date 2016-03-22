$(function () {
  $('#result').hide();
  // get task-id from url
  var task_id = window.location.pathname.match(/\/([0-9a-zA-Z]+)\/?$/)[1];
  var path_prefix = '/media/cellq/task/' + task_id + '/' + task_id;
  // check status
  var poll = function () {
    $.ajax({
      url: '/api/v1/tasks/status?id=' + task_id,
      dataType: 'json',
      type: 'GET',
      traditional: true,
      success: function (data, status) {
        console.log(data);

        if (data.data[0].result_status.toLowerCase() != "success")
          setTimeout(poll, 3000);
        else {
          // get result json data
          $.getJSON(path_prefix + '_out.json', function (result) {
            $('#ratio').text(Math.round(result['ratio'] * 10000) / 100 + '%');
            $('#count').text(result['count_min']);
          });
          // display image
          // /media/cellq/task/7ef4f4782fc840738f67a43edafc9683/7ef4f4782fc840738f67a43edafc9683_in.jpg
          $('#input-img').attr('src', '/media/cellq/task/' + task_id + '/' + task_id + '_in.jpg');
          $('#input-download').attr('href', '/media/cellq/task/' + task_id + '/' + task_id + '_in.jpg');
          $('#result-img').attr('src', '/media/cellq/task/' + task_id + '/' + task_id + '_out.jpg');
          $('#result-download').attr('href', '/media/cellq/task/' + task_id + '/' + task_id + '_out.jpg');

          // get image size
          $("<img/>") // Make in memory copy of image to avoid css issues
            .attr("src", $('#input-img').attr("src"))
            .load(function () {
              var img_w = this.width;   // Note: $(this).width() will not
              var img_h = this.height; // work for in memory images.

              // window resize
              var frame_w = ($(window).width() - 100) / 2;
              $('div.parent').width(frame_w);
              $('div.parent').height(frame_w / img_w * img_h);
              //console.log(img_w, img_h, frame_w, frame_w / img_w * img_h, $('#input-img').attr("src"))
              console.log(frame_w / img_w);
              var $section = $('#result');
              var $panzoom = $section.find('.panzoom').panzoom({
                $set: $section.find('.panzoom'),
                //startTransform: 'scale(' + (frame_w / img_w + 0.01) + ')',
                //increment: 0.01,
                minScale: frame_w / img_w,
                maxScale: 2.0,
                contain: 'invert',
              });
              $panzoom.parent().on('mousewheel.focal', function (e) {
                e.preventDefault();
                var delta = e.delta || e.originalEvent.wheelDelta;
                var zoomOut = delta ? delta < 0 : e.originalEvent.deltaY > 0;
                $panzoom.panzoom('zoom', zoomOut, {
                  increment: 0.02,
                  animate: false,
                  focal: e
                });
              });
              var lazyLayout = _.throttle(function () {
                // get image size
                $("<img/>") // Make in memory copy of image to avoid css issues
                  .attr("src", $('#input-img').attr("src"))
                  .load(function () {
                    var img_w = this.width;   // Note: $(this).width() will not
                    var img_h = this.height; // work for in memory images.

                    // window resize
                    var frame_w = ($(window).width() - 100) / 2;
                    $('div.parent').width(frame_w);
                    $('div.parent').height(frame_w / img_w * img_h);
                    //console.log(img_w, img_h, frame_w, frame_w / img_w * img_h, $('#input-img').attr("src"))
                    console.log(frame_w / img_w);
                  });
              }, 200, { leading: false });
              $(window).resize(lazyLayout);
            });
          $('#result').fadeIn(1000);
          $('#cover').fadeOut(1000);
        }
      }
    });
  };
  poll();
});