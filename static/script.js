// static/js/script.js - Logika Jadwal CRUD menggunakan API Flask

// Peta Hari Indonesia ke Index
const DAY_MAP = {
  "Senin": 1, "Selasa": 2, "Rabu": 3, "Kamis": 4,
  "Jumat": 5, "Sabtu": 6, "Minggu": 7
};

// --- Fungsi Helper API ---

async function fetchSchedules() {
  try {
    const response = await fetch('/api/schedules');
    if (!response.ok) throw new Error('Failed to fetch schedules');
    return await response.json();
  } catch (error) {
    console.error("Error fetching schedules:", error);
    return [];
  }
}

async function saveSchedule(scheduleData, isUpdate = false, id = null) {
  const method = isUpdate ? 'PUT' : 'POST';
  const url = isUpdate ? `/api/schedules/${id}` : '/api/schedules';
  try {
    const response = await fetch(url, {
      method: method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(scheduleData),
    });
    if (!response.ok) throw new Error('Failed to save schedule');
    return await response.json();
  } catch (error) {
    console.error("Error saving schedule:", error);
    alert(`Gagal menyimpan jadwal: ${error.message}`);
    return null;
  }
}

async function deleteScheduleAPI(id) {
  try {
    const response = await fetch(`/api/schedules/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete schedule');
    return await response.json();
  } catch (error) {
    console.error("Error deleting schedule:", error);
    alert(`Gagal menghapus jadwal: ${error.message}`);
    return null;
  }
}

// --- Logika Jadwal (CRUD Client-Side) ---

function createScheduleRow(schedule) {
  const row = document.createElement("tr");
  // ID diambil dari database (dari properti 'id' object schedule)
  row.dataset.scheduleId = schedule.id;
  row.innerHTML = `
        <td>${schedule.day}</td>
        <td>${schedule.time}</td>
        <td>${schedule.subject}</td>
        <td>${schedule.notes || ''}</td>
        <td>
            <button class="action-btn edit-btn" onclick="editSchedule(${schedule.id}, this)">Edit</button>
            <button class="action-btn delete-btn" onclick="deleteSchedule(${schedule.id})">Delete</button>
        </td>
    `;
  return row;
}

async function loadSchedules() {
  const schedules = await fetchSchedules();
  const tableBody = document.getElementById("schedule-list");
  if (!tableBody) return;

  // Logika Filtering Sederhana (Client-side)
  const filterMode = document.getElementById('schedule-filter')?.value || 'all';
  const filterDay = document.getElementById('schedule-filter-day')?.value || '';
  let toRender = schedules.slice();

  if (filterMode === 'today') {
    const today = new Date().toLocaleDateString('id-ID', { weekday: 'long' });
    toRender = toRender.filter(s => s.day && s.day.toLowerCase() === today.toLowerCase());
  } else if (filterMode === 'day' && filterDay) {
    toRender = toRender.filter(s => s.day && s.day.toLowerCase() === filterDay.toLowerCase());
  }

  // Urutkan (Karena query API sudah mengurutkan, langkah ini opsional)
  toRender.sort((a, b) => {
    const dayA = DAY_MAP[a.day] || 8;
    const dayB = DAY_MAP[b.day] || 8;
    if (dayA !== dayB) return dayA - dayB;
    return (a.time || '').localeCompare(b.time || '');
  });

  tableBody.innerHTML = '';
  toRender.forEach((s) => {
    tableBody.appendChild(createScheduleRow(s));
  });

  // Update Overview (jika ada elemennya di dashboard)
  updateOverview();
}

async function addOrUpdateSchedule() {
  const subjectEl = document.getElementById("matkulName");
  const dayEl = document.getElementById("matkulDay");
  const timeEl = document.getElementById("matkulTime");
  const notesEl = document.getElementById("matkulKet");
  const schedForm = document.getElementById("schedule-input-form");

  if (!subjectEl || !dayEl || !timeEl) return;

  const subject = subjectEl.value.trim();
  const day = dayEl.value.trim();
  const time = timeEl.value.trim();
  const notes = notesEl ? notesEl.value.trim() : "";
  const editId = schedForm.dataset.editId;

  if (!subject || !day || !time) {
    alert("Nama Mata Pelajaran, Hari, dan Jam wajib diisi!");
    return;
  }

  const scheduleData = { subject, day, time, notes };
  let result = null;

  if (editId) {
    // UPDATE
    result = await saveSchedule(scheduleData, true, parseInt(editId, 10));
  } else {
    // CREATE
    result = await saveSchedule(scheduleData, false);
  }

  if (result) {
    // Reload dan reset form
    loadSchedules();
    resetScheduleForm();
    schedForm.classList.add("hidden");
  }
}

async function deleteSchedule(id) {
  if (!confirm("Yakin ingin menghapus jadwal ini?")) return;

  const result = await deleteScheduleAPI(id);
  if (result) {
    loadSchedules();
  }
}

// Edit schedule: prefill form and set edit ID
function editSchedule(id, buttonEl) {
  const row = buttonEl.closest('tr');
  if (!row) return;

  // Ambil data dari baris tabel (Ini asumsi, lebih baik ambil dari API jika data kompleks)
  // Karena kita tidak menyimpan semua data jadwal di memori client, kita harus mencari data dari API, 
  // tetapi untuk demo, kita bisa mengambil dari baris tabel jika strukturnya sesuai.
  // Index 0: Hari, 1: Jam, 2: Mapel, 3: Catatan

  const cells = row.querySelectorAll('td');
  const s = {
    subject: cells[2].textContent,
    day: cells[0].textContent,
    time: cells[1].textContent,
    notes: cells[3].textContent,
  };

  const schedForm = document.getElementById('schedule-input-form');
  if (!schedForm) return;

  document.getElementById('matkulName').value = s.subject || '';
  document.getElementById('matkulDay').value = s.day || '';
  document.getElementById('matkulTime').value = s.time || '';
  document.getElementById('matkulKet').value = s.notes || '';

  // Set ID jadwal yang akan diedit
  schedForm.dataset.editId = id;
  const saveBtn = document.getElementById('schedule-save-btn');
  if (saveBtn) saveBtn.textContent = 'Simpan Perubahan';

  // Tampilkan form
  schedForm.classList.remove('hidden');
}

function resetScheduleForm() {
  const schedForm = document.getElementById("schedule-input-form");
  if (schedForm) {
    document.getElementById('matkulName').value = '';
    document.getElementById('matkulDay').value = '';
    document.getElementById('matkulTime').value = '';
    document.getElementById('matkulKet').value = '';
    schedForm.dataset.editId = '';
    const saveBtn = document.getElementById('schedule-save-btn');
    if (saveBtn) saveBtn.textContent = 'Simpan';
  }
}

function onScheduleFilterChange() {
  const sel = document.getElementById('schedule-filter');
  const daySel = document.getElementById('schedule-filter-day');
  if (!sel || !daySel) return;
  if (sel.value === 'day') {
    daySel.style.display = 'inline-block';
  } else {
    daySel.style.display = 'none';
    // Auto apply filter when selecting 'all' or 'today'
    applyScheduleFilter();
  }
}

function applyScheduleFilter() {
  loadSchedules();
}

// --- Logika Overview (Sederhana untuk demo) ---

async function updateOverview() {
  try {
    const response = await fetch('/api/overview');
    if (!response.ok) throw new Error('Failed to fetch overview data');
    const data = await response.json();

    // Tugas Belum Selesai
    const pendingEl = document.getElementById("pending-tasks-count");
    if (pendingEl) pendingEl.textContent = data.pending_count;

    // Jadwal Terdekat
    const closestInfoEl = document.getElementById("closest-schedule-info");
    const closestTimeEl = document.getElementById("closest-schedule-time"); // Perlu elemen ini di dashboard.html

    if (data.closest_schedule) {
      if (closestInfoEl) closestInfoEl.textContent = `${data.closest_schedule.subject}`;
      // Asumsi: Jika jadwal hari ini ditemukan, tampilkan jamnya.
      if (closestTimeEl) closestTimeEl.textContent = `${data.closest_schedule.time || ''} - Hari ini`;
    } else {
      if (closestInfoEl) closestInfoEl.textContent = "Tidak ada jadwal hari ini";
      if (closestTimeEl) closestTimeEl.textContent = "";
    }

  } catch (error) {
    console.error("Error updating overview:", error);
  }
}


// =======================================================================
// --- 6. Logika Penjadwalan Tugas ---
// =======================================================================

function createStatusIndicator(isDone) {
  const statusText = isDone ? "Selesai" : "Belum Selesai";
  const statusClass = isDone ? "status-done" : "status-pending";

  return `<span class="status-indicator ${statusClass}">${statusText}</span>`;
}

function createTaskRow(task, index) {
  const row = document.createElement("tr");
  row.dataset.originalIndex = index;
  // Tambahkan class 'done' untuk efek abu-abu muda (Poin 6 Note)
  if (task.done) {
    row.classList.add("task-row", "done");
  } else {
    row.classList.add("task-row");
  }

  row.innerHTML = `
        <td>${task.subject}</td>
        <td>${task.name}</td>
        <td onclick="toggleTaskStatus(${index})">${createStatusIndicator(
    task.done
  )}</td>
        <td>${formatDate(task.deadline)}</td>
        <td>${task.notes}</td>
        <td>
            <button class="action-btn edit-btn" onclick="editTask(${index})">Edit</button>
            <button class="action-btn delete-btn" onclick="deleteTask(${index})">Delete</button>
        </td>
    `;
  return row;
}

function loadTasks() {
  // Memuat data tanpa filter, kemudian menjalankan filter untuk tampilan awal
  const tasks = getSavedData("tasks");
  const tableBody = document.getElementById("task-list");
  if (!tableBody) return; // nothing to render on this page
  tableBody.innerHTML = "";

  tasks.forEach((t, index) => {
    tableBody.appendChild(createTaskRow(t, index));
  });
  updateOverview();
}

function addTask() {
  const subjEl = document.getElementById("tugasPel");
  const nameEl = document.getElementById("tugasName");
  const deadlineEl = document.getElementById("tugasDeadline");
  const notesEl = document.getElementById("tugasKet");

  if (!subjEl || !nameEl || !deadlineEl) {
    alert("Form tugas tidak ditemukan pada halaman ini.");
    return;
  }

  const subject = subjEl.value.trim();
  const name = nameEl.value.trim();
  const deadline = deadlineEl.value; // YYYY-MM-DD
  const notes = notesEl ? notesEl.value.trim() : "";

  if (!subject || !name || !deadline) {
    alert("Mata Pelajaran, Nama Tugas, dan Deadline wajib diisi!");
    return;
  }

  const tasks = getSavedData("tasks");
  tasks.push({ subject, name, deadline, notes, done: false });
  saveData("tasks", tasks);

  // Reload dan reset form
  loadTasks();
  const assignForm = document.getElementById("assignment-input-form");
  if (assignForm) assignForm.classList.add("hidden");
}

function toggleTaskStatus(id) {
  let tasks = getSavedData("tasks");
  // Poin 6 Note: Jika diklik, status berubah dari Belum Selesai menjadi Selesai.
  tasks[id].done = !tasks[id].done;
  saveData("tasks", tasks);
  loadTasks();
}

function deleteTask(id) {
  if (!confirm("Yakin ingin menghapus tugas ini?")) return;

  let tasks = getSavedData("tasks");
  tasks.splice(id, 1);
  saveData("tasks", tasks);
  loadTasks();
}

// Logika Filter Tugas (Poin 6.b)
function filterTasks() {
  const statusFilterEl = document.getElementById("task-status-filter");
  const deadlineFilterEl = document.getElementById("task-deadline-filter");
  const matkulFilterEl = document.getElementById("task-matkul-filter");
  const statusFilter = statusFilterEl ? statusFilterEl.value : 'all';
  const deadlineFilter = deadlineFilterEl ? deadlineFilterEl.value : 'all';
  const matkulFilter = matkulFilterEl ? matkulFilterEl.value : 'all';
  const originalTasks = getSavedData("tasks");
  const tableBody = document.getElementById("task-list");
  tableBody.innerHTML = "";
  // Determine deadline value (accept either 'deadline' or 'duedate')
  function getDeadlineDate(task) {
    const d = task.deadline || task.duedate || task.dueDate || '';
    if (!d) return null;
    // parse as local date to avoid timezone issues
    return new Date(d + 'T00:00:00');
  }

  let filteredTasks = originalTasks.filter((task) => {
    // Filter berdasarkan Status
    const statusMatch =
      statusFilter === "all" ||
      (statusFilter === "pending" && !task.done) ||
      (statusFilter === "done" && task.done);

    // Filter berdasarkan Mata Kuliah
    const matkulMatch = matkulFilter === "all" || task.subject === matkulFilter;

    // Filter berdasarkan Deadline
    let deadlineMatch = true;
    if (deadlineFilter === 'nearest') {
      const dl = getDeadlineDate(task);
      if (!dl) deadlineMatch = false;
      else {
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const max = new Date(today);
        max.setDate(max.getDate() + 7);
        deadlineMatch = dl >= today && dl <= max;
      }
    }

    return statusMatch && matkulMatch && deadlineMatch;
  });

  // Tampilkan tugas yang sudah difilter
  filteredTasks.forEach((task) => {
    // Gunakan index asli untuk memastikan aksi (delete/toggle) berjalan pada data yang benar di localStorage
    const originalIndex = originalTasks.findIndex(
      (t) => t.subject === task.subject && t.name === task.name
    );
    if (originalIndex !== -1) {
      tableBody.appendChild(createTaskRow(task, originalIndex));
    }
  });
}

function resetTaskFilters() {
  const status = document.getElementById('task-status-filter'); if (status) status.value = 'all';
  const deadline = document.getElementById('task-deadline-filter'); if (deadline) deadline.value = 'all';
  const matkul = document.getElementById('task-matkul-filter'); if (matkul) matkul.value = 'all';
  loadTasks();
}

// --- Dashboard preview renderers ---
function renderDashboardTasks(tasks) {
  const tbody = document.getElementById('dashboard-task-list');
  if (!tbody) return;
  tbody.innerHTML = '';
  const sorted = tasks.slice().sort((a, b) => (a.done === b.done) ? 0 : (a.done ? 1 : -1));
  const show = sorted.slice(0, 5);
  show.forEach(t => {
    const tr = document.createElement('tr');
    const dLine = t.duedate || t.deadline || '';
    tr.innerHTML = `<td>${t.subject || ''}</td><td>${t.name || ''}</td><td>${formatDate(dLine)}</td>`;
    tbody.appendChild(tr);
  });
}

function renderDashboardSchedules(schedules) {
  const tbody = document.getElementById('dashboard-schedule-list');
  if (!tbody) return;
  tbody.innerHTML = '';
  const dayOrder = ['senin', 'selasa', 'rabu', 'kamis', 'jumat', 'sabtu', 'minggu'];
  const normalized = schedules.slice().filter(s => s.day).map(s => ({ day: s.day, time: s.time || '', subject: s.subject || '' }));
  normalized.sort((a, b) => {
    const da = dayOrder.indexOf((a.day || '').toLowerCase());
    const db = dayOrder.indexOf((b.day || '').toLowerCase());
    if (da !== db) return da - db;
    return (a.time || '').localeCompare(b.time || '');
  });
  normalized.slice(0, 5).forEach(s => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${s.day}</td><td>${s.time}</td><td>${s.subject}</td>`;
    tbody.appendChild(tr);
  });
}