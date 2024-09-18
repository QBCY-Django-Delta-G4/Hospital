// ناپدید شدن پیام‌ها بعد از ۳ ثانیه
document.querySelectorAll('.messages li').forEach(function(message) {
    setTimeout(function() {
        message.style.opacity = '0'; // به تدریج ناپدید می‌شود
        setTimeout(function() {
            message.remove(); // حذف کامل پیام از DOM
        }, 1000); // زمان تطابق با transition
    }, 1530); // 3 ثانیه برای نمایش
});