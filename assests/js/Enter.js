        document.addEventListener('keydown', function(event) {
            if (event.ctrlKey && event.key === 'Enter') {
                event.preventDefault(); // جلوگیری از عملیات پیش‌فرض
                document.getElementById('commentForm').submit(); // ارسال فرم
            }
        });