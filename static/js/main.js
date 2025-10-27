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
    // Cart functionality
    $(document).ready(function() {
        // Add to cart with AJAX
        $('.add-to-cart-form').on('submit', function(e) {
            e.preventDefault();
            const form = $(this);
            const button = form.find('.add-to-cart-btn');
            const originalText = button.html();

            button.prop('disabled', true);
            button.html('<span class="loading-spinner"></span> Adding...');

            $.ajax({
                type: 'POST',
                url: form.attr('action'),
                data: form.serialize(),
                success: function(response) {
                    if (response.success) {
                        button.html('<i class="fas fa-check me-2"></i>Added!');
                        updateCartSummary(response.cart_summary);
                        showToast('Product added to cart!', 'success');
                    } else {
                        button.html(originalText);
                        button.prop('disabled', false);
                        showToast(response.message, 'error');
                    }
                },
                error: function() {
                    button.html(originalText);
                    button.prop('disabled', false);
                    showToast('Error adding product to cart', 'error');
                }
            });
        });

        // Update cart summary in navigation
        function updateCartSummary(summary) {
            $('.cart-count').text(summary.total_items);

            // Update cart dropdown if open
            const cartDropdown = $('#cartDropdown');
            if (cartDropdown.next('.dropdown-menu').is(':visible')) {
                // You might want to refresh the cart dropdown content here
                // For now, we'll just update the count
            }
        }

        // Toast notification
        function showToast(message, type = 'info') {
            // Simple toast implementation
            const toast = $(`
                <div class="toast align-items-center text-white bg-${type === 'success' ? 'success' : 'danger'} border-0 position-fixed top-0 end-0 m-3" role="alert">
                    <div class="d-flex">
                        <div class="toast-body">${message}</div>
                        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                    </div>
                </div>
            `);

            $('body').append(toast);
            const bsToast = new bootstrap.Toast(toast[0]);
            bsToast.show();

            toast.on('hidden.bs.toast', function() {
                $(this).remove();
            });
        }

        // Quantity input controls
        $('.quantity-plus').click(function() {
            const input = $(this).siblings('input[type="number"]');
            const max = parseInt(input.attr('max'));
            let value = parseInt(input.val()) + 1;
            if (value <= max) {
                input.val(value);
            }
        });

        $('.quantity-minus').click(function() {
            const input = $(this).siblings('input[type="number"]');
            const min = parseInt(input.attr('min'));
            let value = parseInt(input.val()) - 1;
            if (value >= min) {
                input.val(value);
            }
        });
    });

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