var Cookie = {
    set: function (key, val, exp) {
        if (exp) {
            var date = new Date();
            date.setTime(date.getTime() + exp * 3600 * 1000); // 单位:时
            var expiresStr = "expires=" + date.toGMTString() + ';';
        } else {
            var expiresStr = '';
        }
        document.cookie = key + '=' + escape(val) + ';' + expiresStr;
    },
    get: function (key) {
        var arr1 = document.cookie.split("; ");
        for (var i = 0; i < arr1.length; i++) {
            var arr2 = arr1[i].split("=");
            if (arr2[0] == key) {
                return decodeURI(arr2[1]);
            }
        }
    }
};