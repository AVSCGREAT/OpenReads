// Slick#1.6.0 is not on npm
import '../../../../../vendor/js/slick/slick-1.6.0.min.js';
import '../../../../../static/css/components/carousel--js.less';
import Carousel from './Carousel';

/**
 * @param {jQuery.Object} $carouselElements
 */
export function init($carouselElements) {
    $carouselElements.each(function (_i, carouselElement) {
        Carousel.add.apply(Carousel,
            JSON.parse(carouselElement.dataset.config)
        );
    });
}
