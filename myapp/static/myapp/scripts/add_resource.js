var numAuthors = 1;

// Insert a new author field after before the button
function addAuthorField() {
    numAuthors += 1;
    document.getElementById("num_authors").setAttribute("value", numAuthors);

    let authorField = document.createElement("div");
    authorField.id = `author${numAuthors}`;
    authorField.className = "row";
    authorField.innerHTML =
    `<p class="form-label">Author ${numAuthors}</p>

    <div class="col-md-6 mb-3">
        <label class="form-label" for="author${numAuthors}_first_name">First Name (required):</label>
        <input class="form-control" type="text" id="author${numAuthors}_first_name" name="author${numAuthors}_first_name" required>
    </div>

    <div class="col-md-6 mb-3">
        <label class="form-label" for="author${numAuthors}_last_name">Last Name (required):</label>
        <input class="form-control" type="text" id="author${numAuthors}_last_name" name="author${numAuthors}_last_name" required>
    </div>`;

    let button = document.getElementById("add_author");
    button.parentNode.insertBefore(authorField, button);
}

// Remove the last author field
function removeAuthorField() {
    if (numAuthors == 1) return;
    document.getElementById(`author${numAuthors}`).remove();
    numAuthors -= 1;
}