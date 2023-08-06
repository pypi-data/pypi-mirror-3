/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2011
-----------------------------------------------------------------------------*/

cocktail.bind({
    selector: ".ImageGallery",
    behavior: function ($imageGallery) {
 
        var inDialog = false;
        var loadedImages = {};
        var singleImage = ($imageGallery.find(".image_entry").length < 2);

        $imageGallery.bind("imageLoaded", function (e, loadedImage) {
            loadedImages[loadedImage.src] = loadedImage;
        });

        this.loadImage = function (src, callback /* optional */, showStatus /* optional */) {

            var image = loadedImages[src];

            if (image && image.loaded) {
                if (callback) {
                    callback.call(this, image);                    
                }                
            }
            else {
                if (showStatus) {
                    this.setLoading(true);
                }

                if (callback) {
                    var handler = function (e, loadedImage) {
                        if (loadedImage.src == src) {
                            $imageGallery.unbind("imageLoaded", handler);
                            callback.call(this, loadedImage);
                        }
                    }
                    $imageGallery.bind("imageLoaded", handler);
                }
                
                if (!image) {
                    image = new Image();
                    loadedImages[src] = image;
                    image.onload = function () {
                        this.loaded = true;
                        if (image.showStatus) {
                            $imageGallery.get(0).setLoading(false);
                        }
                        $imageGallery.trigger("imageLoaded", this);
                    }
                    image.showStatus = showStatus;
                    image.src = src;
                }
                else if (showStatus) {
                    image.showStatus = true;
                }
            }
        }

        this.setLoading = function (loading) {
            var $sign = jQuery(".ImageGallery-loading_sign");

            if (!loading) {
                clearInterval($sign.get(0).animationTimer);
                $sign.remove();
            }
            else if (!$sign.length) {
                var sign = cocktail.instantiate("woost.views.ImageGallery.loading_sign");
                sign.animationStep = 0;
                sign.ball = document.createElement("div");
                sign.ball.className = "ball";
                sign.appendChild(sign.ball);
                sign.animationTimer = setInterval(function () {
                    sign.animationStep = (sign.animationStep + 1) % 200;
                    if (sign.animationStep < 100) {
                        var pos = sign.animationStep;
                    }
                    else {
                        var pos = 200 - sign.animationStep;
                    }
                    sign.ball.style.left = sign.offsetWidth / 4 + (sign.offsetWidth / 2 * pos / 100) + "px";
                }, 10);
                document.body.appendChild(sign);
                cocktail.center(sign);
            }
        }

        this.pauseAutoplay = function () {
            // Temporarely disable the automatic slideshow, until the user
            // closes the dialog
            if (this.sudoSlider && this.sliderOptions.auto) {
                this.sudoSlider.stopAuto();
            }
        }

        this.resumeAutoplay = function () {
            // Resume the automatic slideshow
            if (this.sudoSlider && this.sliderOptions.auto && !inDialog) {
                this.sudoSlider.startAuto();
            }
        }

        $imageGallery.hover(this.pauseAutoplay, this.resumeAutoplay);

        this.showImage = function (entry) {
            
            inDialog = true;
            this.pauseAutoplay();

            cocktail.closeDialog();
            var dialog = this.createImageDialog(entry);
            cocktail.showDialog(dialog);            
            var $dialog = jQuery(dialog);
            $dialog.hide();

            // Show the dialog once the image finishes loading            
            this.loadImage(
                jQuery(entry).find(".image_link").get(0).href,
                function (image) {
                    $dialog.find(".image")
                        .width(image.width)
                        .height(image.height);
                    $dialog.show();
                    cocktail.center(dialog);
                    $dialog
                        .hide()
                        .fadeIn()
                        .find(".image[tabindex=0]").focus();
                },
                true
            );

            // Synchronize the gallery and the image dialog
            if (this.sudoSlider) {
                this.sudoSlider.goToSlide(jQuery(entry).index() + 1);
            }
        }

        this.showPreviousImage = function (entry) {
            var $entries = $imageGallery.find(".image_entry");
            var prev = jQuery(entry).prev(".image_entry").get(0) 
                    || jQuery(entry).parent().find(".image_entry:last").get(0);
            this.showImage(prev);
        }

        this.showNextImage = function (entry) {
            var $entries = $imageGallery.find(".image_entry");
            var next = jQuery(entry).next(".image_entry").get(0)
                    || jQuery(entry).parent().find(".image_entry").get(0);
            this.showImage(next);
        }

        this.createImageDialog = function (entry) {
        
            if (!entry) {
                return;
            }

            var $entry = jQuery(entry);
            var imageURL = $entry.find(".image_link").attr("href");
            var imageTitle = $entry.find(".image_label").html();

            var $dialog = jQuery(cocktail.instantiate("woost.views.ImageGallery.image_dialog"));

            $dialog.bind("dialogClosed", function () {
                inDialog = false;
                $entry.find(".image_link").focus();
                var ig = $imageGallery.get(0).resumeAutoplay();
            });

            $dialog.find(".image").attr("src", imageURL);
            
            if (imageTitle) {
                $dialog.find(".header .label").html(imageTitle);
            }

            if (singleImage) {
                $dialog.find(".header .index").hide();
            }
            else {
                $dialog.find(".header .index").html(
                    ($entry.index() + 1) + " / " + $imageGallery.find(".image_entry").length
                );
            }

            if (entry.footnote) {
                $dialog.find(".footnote").html(entry.footnote);
            }
            else {
                $dialog.find(".footnote").hide();
            }

            if (entry.originalImage) {
                var $originalLink = $dialog.find(".original_image_link");
                $originalLink.find("a").attr("href", entry.originalImage);
                $originalLink.show();
            }
            else {
                $dialog.find(".original_image_link").hide();
            }

            var $close = $dialog.find(".close_button");
            var $next = $dialog.find(".next_button");
            var $prev = $dialog.find(".previous_button");
            var $img = $dialog.find(".image");
            var $dialogControls = $dialog.find(".header").add($close);
            
            // Close dialog button
            $close.click(cocktail.closeDialog);

            // Image cycling
            if (singleImage) {
                $next.hide();
                $prev.hide();
                $img.attr("tabindex", "-1");
            }
            else {
                $dialogControls = $dialogControls.add($next).add($prev);

                // Next button
                $next.click(function () {
                    $imageGallery.get(0).showNextImage(entry);
                });

                // Previous button
                $prev.click(function () {
                    $imageGallery.get(0).showPreviousImage(entry);
                });

                $img
                    // Keyboard controls
                    .attr("tabindex", "0")
                    .keydown(function (e) {
                        // Right: show next image
                        if (e.keyCode == 39) {
                            $imageGallery.get(0).showNextImage(entry);
                            return false;
                        }
                        // Left: show previous image
                        else if (e.keyCode == 37) {
                            $imageGallery.get(0).showPreviousImage(entry);
                            return false;
                        }
                        // Home: show first image
                        else if (e.keyCode == 36) {
                            $imageGallery.get(0).showImage($imageGallery.find(".image_entry").get(0));
                            return false;
                        }
                        // End: show last image
                        else if (e.keyCode == 35) {
                            $imageGallery.get(0).showImage($imageGallery.find(".image_entry").last().get(0));
                            return false;
                        }
                    })
                    // Click the image to show the next image
                    .click(function () {
                        $imageGallery.get(0).showNextImage(entry);
                    });
            }
            
            // Only show dialog controls when hovering over the image
            $dialogControls.filter(":not(.header)").hide();
            var hideHeaderTimer = setTimeout(
                function () { $dialog.find(".header").fadeOut(); },
                1500
            );

            $dialog.hover(
                function () {
                    $dialogControls.show();
                    if (hideHeaderTimer) {
                        clearTimeout(hideHeaderTimer);
                        hideHeaderTimer = null;
                    }
                },
                function () {
                    $dialogControls.hide();
                }
            );

            return $dialog.get(0);
        }

        if (this.galleryType == "slideshow" && !singleImage) {

            this.sliderOptions.prevHtml = 
                cocktail.instantiate("woost.views.ImageGallery.previous_button");

            this.sliderOptions.nextHtml = 
                cocktail.instantiate("woost.views.ImageGallery.next_button");

            this.sudoSlider = $imageGallery.sudoSlider(this.sliderOptions);

            // Move the navigation controls created by Sudo Slider into the gallery
            $imageGallery.next()
                .addClass("slideshow_controls")
                .appendTo($imageGallery);
        }

        // Image pre-loading
        if (this.closeUpPreload) {
            $imageGallery.find(".image_entry .image_link").each(function () {
                $imageGallery.get(0).loadImage(this.href);
            });
        }
    },
    children: {
        ".image_entry": function ($entry, $imageGallery) {

            var $link = $entry.find(".image_link");
            
            $link.click(function () {
                $imageGallery.get(0).showImage($entry.get(0));
                return false;
            });
        }
    }
});

