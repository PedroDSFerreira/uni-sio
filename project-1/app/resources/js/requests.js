function submitComment() {
    var name = document.getElementById("comment_name").value;
    var email = document.getElementById("comment_email").value;
    var phone = document.getElementById("comment_phone").value;
    var message = document.getElementById("comment_message").value;

    body = {
        "name": name,
        "email": email,
        "phone": phone,
        "message": message
    };

    $.post("/api/contact_us", body)
        .done(function () {
            // Reload page
            location.reload();
        })
        .fail(function () {
            console.log("fail");
        });

}

function queryResults() {
    var query = document.getElementById("query").value;

    if (query.length > 0) {
        body = {
            "query": query
        };
    
        $.get("/api/query_services", body)
            .done(function (result) {
                // Toggle visibility of results if not open
                if (document.getElementById("search_services").style.display == 'none') {
                    changeVisibility("search_services");
                }

                data = JSON.parse(result);
                // Dinamically insert reviews in table
                var table = document.getElementById("search_results");
                // clear table except header
                for (var i = table.rows.length - 1; i > 0; i--) {
                    table.deleteRow(i);
                }
                for (var i = 0; i < data.length; i++) {
                    var row = table.insertRow(i+1);
                    var name = row.insertCell(0);
                    var description = row.insertCell(1);
                    
                    name.innerHTML = data[i][1];
                    description.innerHTML = data[i][2];
                }
                // clear query
                document.getElementById("query").value = "";
            })
            .fail(function () {
                console.log("fail");
            });
    }
}

function search() {
    var query = document.getElementById("search").value;
    window.location.href = "/search?query=" + query;
}

function submitReview() {
    var name = document.getElementById("review_name").value;
    var email = document.getElementById("review_email").value;
    var message = document.getElementById("review_message").value;

    body = {
        "name": name,
        "email": email,
        "message": message
    };

    $.post("/api/review", body)
        .done(function () {
            // Reload page
            location.reload();
        })
        .fail(function () {
            console.log("fail");
        });

}

function getReviews() {
    $.get("/api/get_reviews")
        .done(function (result) {
            data = JSON.parse(result);

            // Dinamically insert reviews in table
            var table = document.getElementById("reviews_table");
            // clear table except header
            for (var i = table.rows.length - 1; i > 0; i--) {
                table.deleteRow(i);
            }
            for (var i = 0; i < data.length; i++) {
                var row = table.insertRow(i+1);
                var name = row.insertCell(0);
                var message = row.insertCell(1);
                
                name.innerHTML = data[i][1];
                message.innerHTML = data[i][3];
            }
        })
        .fail(function () {
            console.log("fail");
        });
}

function submitCode() {
    var code = document.getElementById("code").value;

    body = {
        "code": code
    };

    $.post("/api/get_test_result", body)
        .done(function (data) {
            // decode in base64, check if is valid and download pdf
            var decoded = atob(data);
            if (decoded.length > 0) {
                var link = document.createElement('a');
                link.href = 'data:application/pdf;base64,' + data;
                link.download = "test_result.pdf";
                link.click();
            }
        })
        .fail(function () {
            console.log("fail");
        });

}