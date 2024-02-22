function drag(e) {
    e.dataTransfer.setData("text", e.target.parentNode.id);
}

async function drop(e, el) {
    e.preventDefault();
    const data = e.dataTransfer.getData("text");

    el.appendChild(document.getElementById(data));

    const listID = el.parentNode.dataset.id;
    const taskId = parseInt(data);

    if (e.target.className == "tasks") e.target.style.border = "2px solid #fff";

    await fetch(`/task/update-list/${taskId}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken,
        },
        body: JSON.stringify({
            listID: listID || null,
        }),
    });

    window.location.reload();
}

function allowDrop(e) {
    e.preventDefault();
}

function dragEnter(e) {
    e.preventDefault();
    if (e.target.className == "tasks")
        e.target.style.border = "2px dashed #000";
}

function dragLeave(e) {
    e.preventDefault();
    if (e.target.className == "tasks") e.target.style.border = "2px solid #fff";
}
