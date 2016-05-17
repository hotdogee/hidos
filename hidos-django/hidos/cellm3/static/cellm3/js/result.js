$(function () {
  $('#result').hide();
  // get task-id from url
  var task_id = window.location.pathname.match(/\/([0-9a-zA-Z]+)\/?$/)[1];
  var path_prefix = '/media/cellm3/task/' + task_id + '/' + task_id;
  // check status
  var poll = function () {
    $.ajax({
      url: 'api/v1/tasks/' + task_id,
      dataType: 'json',
      type: 'GET',
      traditional: true,
      success: function (data, status) {
        console.log(data);

        if (data.status.toLowerCase() != "success")
          setTimeout(poll, 3000);
        else {
          // get result json data
          $('#count').text(data.ratio);
          // display image
          // /media/image_analysis/task/7ef4f4782fc840738f67a43edafc9683/7ef4f4782fc840738f67a43edafc9683_in.jpg
          $('#input-img').attr('src', '/media/cellm3/task/' + task_id + '/' + task_id + '_in.jpg');
          $('#input-download').attr('href', '/media/cellm3/task/' + task_id + '/' + task_id + '_in.jpg');
          $('#result-img').attr('src', '/media/cellm3/task/' + task_id + '/' + task_id + '_out.jpg');
          $('#result-download').attr('href', '/media/cellm3/task/' + task_id + '/' + task_id + '_out.jpg');


          // get image size
          $("<img/>") // Make in memory copy of image to avoid css issues
            .attr("src", $('#input-img').attr("src"))
            .load(function () {
              var img_w = this.width;   // Note: $(this).width() will not
              var img_h = this.height; // work for in memory images.

              // window resize
              var frame_w = ($('#result').width() - 100) / 2;
              if ($(window).width() <= 600) {
                  frame_w = ($('#result').width() - 100);
              }
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
                    var frame_w = ($('#result').width() - 100) / 2;
                    if ($(window).width() <= 600) {
                        frame_w = ($('#result').width() - 100);
                    }
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
