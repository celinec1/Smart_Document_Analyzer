document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('loginButton').addEventListener('click', login);
    document.getElementById('registerButton').addEventListener('click', register);


});

function sendRequest(url, method, data, callback) {
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => callback(data))
    .catch(error => console.error('Error:', error));
}

function login() {
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    sendRequest('/login', 'POST', { username: username, password: password }, function(response) {
        if (response.message === "Authentication approved") {
            window.location.href = '/'; // Redirect to home which will show documents page
        } else {
            displayResponse(response);
        }
    });
}

function register() {
    const username = document.getElementById('registerUsername').value;
    const password = document.getElementById('registerPassword').value;
    sendRequest('/register', 'POST', { username: username, password: password }, displayResponse);
}

function displayResponse(response) {
    const responseElement = document.getElementById('response');
    if (response.message) {
        responseElement.innerText = 'Success: ' + response.message;
    } else {
        responseElement.innerText = 'Error: ' + response.error;
    }
}

function createFolder() {
    const folderName = document.getElementById('folderName').value;
    sendRequest('/create_folder', 'POST', { folder_name: folderName }, (response) => {
        if (response.status === "Folder created successfully") {
            // Redirect to home page to see the updated folder list
            window.location.href = '/';
        } else {
            alert(response.error);
        }
    });
}

function deleteFolder(folderName) {
    sendRequest('/delete_folder', 'POST', { folder_name: folderName }, (response) => {
        if (response.status === "Folder and all contained files successfully deleted") {
            // Redirect to home page to see the updated folder list
            window.location.href = '/';
        } else {
            alert(response.error);
        }
    });
}

function logout() {
    window.location.href = '/logout';  
}


document.addEventListener('DOMContentLoaded', function () {
    if (window.location.pathname === '/documents.html') {
        fetchFolders();
    }
});

if (window.location.href === `/files/${folderName}`) {
    fetchFiles(folderName);
}


function fetchFiles(folderName) {
    sendRequest(`/files/${folderName}`, 'GET', {}, (response) => {
        const folderDiv = document.getElementById(folderName);
        folderDiv.innerHTML = ''; // Clear existing file list
        response.files.forEach(file => {
            folderDiv.innerHTML += `<div>${file.file_name} <button onclick="deleteFile('${folderName}', '${file.file_id}')">Delete</button></div>`;
        });
    });
}

function analyzeFile(fileId) {
    const url = `/analyze/${fileId}`;
    window.location.href = url; // Redirects to a new route for analyzing the file
}
