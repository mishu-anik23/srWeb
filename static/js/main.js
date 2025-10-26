// Main JavaScript for Sunrise Supermarkt
$(document).ready(function() {
    // Product image gallery
    $('.thumbnail').click(function() {
        $('.thumbnail').removeClass('active');
        $(this).addClass('active');
        $('#mainImage').attr('src', $(this).attr('src'));
    });

    // Quantity input validation
    $('input[type="number"]').on('input', function() {
        const max = parseInt($(this).attr('max'));
        const min = parseInt($(this).attr('min'));
        let value = parseInt($(this).val());

        if (value > max) {
            $(this).val(max);
        } else if (value < min) {
            $(this).val(min);
        }
    });

    // Add to cart animation
    $('.btn-add-to-cart').click(function(e) {
        e.preventDefault();
        const button = $(this);
        const originalText = button.html();

        button.html('<span class="loading"></span> Adding...');
        button.prop('disabled', true);

        // Simulate API call
        setTimeout(function() {
            button.html('<i class="fas fa-check me-2"></i>Added to Cart');
            button.removeClass('btn-success').addClass('btn-outline-success');

            // Update cart count
            const cartCount = $('.cart-count');
            let count = parseInt(cartCount.text()) || 0;
            cartCount.text(count + 1);

            // Reset button after 2 seconds
            setTimeout(function() {
                button.html(originalText);
                button.prop('disabled', false);
                button.removeClass('btn-outline-success').addClass('btn-success');
            }, 2000);
        }, 1000);
    });

    // Search functionality
    $('#searchForm').submit(function(e) {
        const query = $('#searchInput').val().trim();
        if (query === '') {
            e.preventDefault();
            $('#searchInput').focus();
        }
    });

    // Smooth scrolling for anchor links
    $('a[href^="#"]').click(function(e) {
        e.preventDefault();
        const target = $(this.getAttribute('href'));
        if (target.length) {
            $('html, body').animate({
                scrollTop: target.offset().top - 80
            }, 1000);
        }
    });
});

// Image gallery function
function changeMainImage(imageUrl) {
    document.getElementById('mainImage').src = imageUrl;

    // Update active thumbnail
    const thumbnails = document.querySelectorAll('.thumbnail');
    thumbnails.forEach(thumb => {
        thumb.classList.remove('active');
        if (thumb.src === imageUrl) {
            thumb.classList.add('active');
        }
    });
}