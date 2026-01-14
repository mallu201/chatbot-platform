let token = localStorage.getItem("token");

function showRegister() {
  document.getElementById("loginSection").style.display = "none";
  document.getElementById("registerSection").style.display = "block";
  document.getElementById("message").innerText = "";
}

function showLogin() {
  document.getElementById("registerSection").style.display = "none";
  document.getElementById("loginSection").style.display = "block";
  document.getElementById("message").innerText = "";
}

async function register() {
  const email = document.getElementById("regEmail").value;
  const password = document.getElementById("regPassword").value;
  const msgDiv = document.getElementById("message");

  if (!email || !password) {
    msgDiv.innerText = "Please fill all fields";
    return;
  }

  try {
    const res = await fetch("/users/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    if (res.ok) {
      msgDiv.style.color = "green";
      msgDiv.innerText = "Registration successful! Please login.";
      setTimeout(() => showLogin(), 1500);
    } else {
      msgDiv.style.color = "red";
      msgDiv.innerText = data.detail || "Registration failed";
    }
  } catch (error) {
    msgDiv.style.color = "red";
    msgDiv.innerText = "Error: " + error.message;
  }
}

async function login() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const msgDiv = document.getElementById("message");

  if (!email || !password) {
    msgDiv.innerText = "Please fill all fields";
    return;
  }

  try {
    const res = await fetch("/users/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    if (data.access_token) {
      localStorage.setItem("token", data.access_token);
      window.location.href = "/dashboard";
    } else {
      msgDiv.style.color = "red";
      msgDiv.innerText = data.detail || "Login failed";
    }
  } catch (error) {
    msgDiv.style.color = "red";
    msgDiv.innerText = "Error: " + error.message;
  }
}

// ---------------- CREATE PROJECT ----------------
async function createProject() {
  const name = document.getElementById("projectName").value;

  await fetch("/projects", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + token
    },
    body: JSON.stringify({ name })
  });

  loadProjects();
}

// ---------------- LOAD PROJECTS ----------------
async function loadProjects() {
  const res = await fetch("/projects", {
    headers: {
      "Authorization": "Bearer " + token
    }
  });

  const projects = await res.json();
  const list = document.getElementById("projectList");
  list.innerHTML = "";

  projects.forEach(p => {
    const li = document.createElement("li");
    li.innerText = p.name;
    list.appendChild(li);
  });
}

// Auto load dashboard
if (window.location.pathname === "/dashboard") {
  loadProjects();
}

// ---------------- CHAT ----------------
async function loadProjectsForChat() {
  const select = document.getElementById("projectSelect");
  
  try {
    const res = await fetch("/projects", {
      headers: { "Authorization": "Bearer " + token }
    });

    if (!res.ok) {
      window.location.href = "/";
      return;
    }

    const projects = await res.json();
    select.innerHTML = "";

    if (projects.length === 0) {
      select.innerHTML = "<option value=''>No projects. Create one first.</option>";
      return;
    }

    projects.forEach(p => {
      const option = document.createElement("option");
      option.value = p.id;
      option.textContent = p.name;
      select.appendChild(option);
    });
  } catch (error) {
    select.innerHTML = "<option value=''>Error loading projects</option>";
  }
}

async function sendMessage() {
  const msg = document.getElementById("message").value;
  const projectId = document.getElementById("projectSelect").value;
  const responseDiv = document.getElementById("response");
  const errorDiv = document.getElementById("errorMsg");

  if (!msg) {
    errorDiv.innerText = "Please enter a message";
    return;
  }

  if (!projectId) {
    errorDiv.innerText = "Please select a project";
    return;
  }

  errorDiv.innerText = "";
  responseDiv.innerText = "Thinking...";

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
      },
      body: JSON.stringify({
        project_id: parseInt(projectId),
        message: msg
      })
    });

    let data;
    const contentType = res.headers.get("content-type");
    
    if (contentType && contentType.includes("application/json")) {
      data = await res.json();
    } else {
      const text = await res.text();
      errorDiv.innerText = "Server error: " + text.substring(0, 100);
      responseDiv.innerText = "";
      return;
    }

    if (!res.ok) {
      errorDiv.innerText = data.detail || "Error getting response";
      responseDiv.innerText = "";
    } else {
      responseDiv.innerText = data.reply || "No response";
      document.getElementById("message").value = "";
    }
  } catch (error) {
    errorDiv.innerText = "Error: " + error.message;
    responseDiv.innerText = "";
  }
}

// ---------------- PROMPTS ----------------
async function loadProjectsForPrompts() {
  const select = document.getElementById("promptProjectSelect");
  
  try {
    const res = await fetch("/projects", {
      headers: { "Authorization": "Bearer " + token }
    });

    const projects = await res.json();
    select.innerHTML = "<option value=''>Select a project</option>";

    projects.forEach(p => {
      const option = document.createElement("option");
      option.value = p.id;
      option.textContent = p.name;
      select.appendChild(option);
    });

    select.onchange = loadPrompts;
  } catch (error) {
    console.error("Error loading projects:", error);
  }
}

async function loadPrompts() {
  const projectId = document.getElementById("promptProjectSelect").value;
  const promptsDiv = document.getElementById("promptsList");

  if (!projectId) {
    promptsDiv.innerHTML = "";
    return;
  }

  try {
    const res = await fetch(`/projects/${projectId}/prompts`, {
      headers: { "Authorization": "Bearer " + token }
    });

    const prompts = await res.json();
    promptsDiv.innerHTML = "<h4>Prompts:</h4>";

    if (prompts.length === 0) {
      promptsDiv.innerHTML += "<p>No prompts yet. Create one above.</p>";
      return;
    }

    prompts.forEach(p => {
      const div = document.createElement("div");
      div.style.border = "1px solid #ccc";
      div.style.padding = "10px";
      div.style.margin = "5px 0";
      div.innerHTML = `
        <strong>${p.name}</strong>
        <p>${p.content}</p>
        <button onclick="deletePrompt(${p.id})">Delete</button>
      `;
      promptsDiv.appendChild(div);
    });
  } catch (error) {
    promptsDiv.innerHTML = "<p>Error loading prompts</p>";
  }
}

async function createPrompt() {
  const projectId = document.getElementById("promptProjectSelect").value;
  const name = document.getElementById("promptName").value;
  const content = document.getElementById("promptContent").value;

  if (!projectId || !name || !content) {
    alert("Please fill all fields");
    return;
  }

  try {
    const res = await fetch(`/projects/${projectId}/prompts`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
      },
      body: JSON.stringify({ name, content })
    });

    if (res.ok) {
      document.getElementById("promptName").value = "";
      document.getElementById("promptContent").value = "";
      loadPrompts();
    } else {
      const data = await res.json();
      alert(data.detail || "Error creating prompt");
    }
  } catch (error) {
    alert("Error: " + error.message);
  }
}

async function deletePrompt(promptId) {
  if (!confirm("Delete this prompt?")) return;

  try {
    const res = await fetch(`/projects/prompts/${promptId}`, {
      method: "DELETE",
      headers: { "Authorization": "Bearer " + token }
    });

    if (res.ok) {
      loadPrompts();
    } else {
      alert("Error deleting prompt");
    }
  } catch (error) {
    alert("Error: " + error.message);
  }
}

// ---------------- FILES ----------------
async function loadProjectsForFiles() {
  const select = document.getElementById("fileProjectSelect");
  
  try {
    const res = await fetch("/projects", {
      headers: { "Authorization": "Bearer " + token }
    });

    const projects = await res.json();
    select.innerHTML = "<option value=''>Select a project</option>";

    projects.forEach(p => {
      const option = document.createElement("option");
      option.value = p.id;
      option.textContent = p.name;
      select.appendChild(option);
    });

    select.onchange = loadFiles;
  } catch (error) {
    console.error("Error loading projects:", error);
  }
}

async function loadFiles() {
  const projectId = document.getElementById("fileProjectSelect").value;
  const filesDiv = document.getElementById("filesList");

  if (!projectId) {
    filesDiv.innerHTML = "";
    return;
  }

  try {
    const res = await fetch(`/projects/${projectId}/files`, {
      headers: { "Authorization": "Bearer " + token }
    });

    const files = await res.json();
    filesDiv.innerHTML = "<h4>Uploaded Files:</h4>";

    if (files.length === 0) {
      filesDiv.innerHTML += "<p>No files uploaded yet.</p>";
      return;
    }

    files.forEach(f => {
      const div = document.createElement("div");
      div.style.border = "1px solid #ccc";
      div.style.padding = "10px";
      div.style.margin = "5px 0";
      div.innerHTML = `
        <strong>${f.filename}</strong> (${(f.file_size / 1024).toFixed(2)} KB)
        <button onclick="deleteFile(${f.id})">Delete</button>
      `;
      filesDiv.appendChild(div);
    });
  } catch (error) {
    filesDiv.innerHTML = "<p>Error loading files</p>";
  }
}

async function uploadFile() {
  const projectId = document.getElementById("fileProjectSelect").value;
  const fileInput = document.getElementById("fileInput");

  if (!projectId) {
    alert("Please select a project");
    return;
  }

  if (!fileInput.files || fileInput.files.length === 0) {
    alert("Please select a file");
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  try {
    const res = await fetch(`/projects/${projectId}/files`, {
      method: "POST",
      headers: {
        "Authorization": "Bearer " + token
      },
      body: formData
    });

    if (res.ok) {
      fileInput.value = "";
      loadFiles();
      alert("File uploaded successfully");
    } else {
      const data = await res.json();
      alert(data.detail || "Error uploading file");
    }
  } catch (error) {
    alert("Error: " + error.message);
  }
}

async function deleteFile(fileId) {
  if (!confirm("Delete this file?")) return;

  try {
    const res = await fetch(`/projects/files/${fileId}`, {
      method: "DELETE",
      headers: { "Authorization": "Bearer " + token }
    });

    if (res.ok) {
      loadFiles();
    } else {
      alert("Error deleting file");
    }
  } catch (error) {
    alert("Error: " + error.message);
  }
}
