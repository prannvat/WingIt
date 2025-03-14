function openSetting(event, settingChild) {
    let settingParents = document.getElementsByClassName("setting_select")
    let settingChildren = document.getElementsByClassName("child")
    let thisSettingParent = event.currentTarget

    for(i = 0; i < settingChildren.length; i++) {
        settingChildren[i].style.display = "none";
    }

    for(i = 0; i < settingParents.length; i++) {
        settingParents[i].className = settingParents[i].className.replace(" active", "");
    }

    document.getElementById(settingChild).style.display = "inline";
    thisSettingParent.className += " active";
}

async function setCheckValues() {
    let world = document.getElementById("world_toggle");
    let business = document.getElementById("business_toggle");
    let technology = document.getElementById("technology_toggle");
    let entertainment = document.getElementById("entertainment_toggle");
    let toggles = document.getElementsByClassName("category_toggle");
    
    try {
        const response = await fetch("/settings", {
            method: "GET",
            headers: {
                "Accept": "application/json",
                "originalMethod": "GET",
            }
        });
        const data = await response.json();
        world.value = data.world;
        business.value = data.business;
        technology.value = data.technology;
        entertainment.value = data.entertainment;
    }
    catch (error) {
        alert("An error occured fetching previous settings " + error);
    }
    for(i = 0; i < toggles.length; i++) {
        if(toggles[i].value == 1) {
            toggles[i].checked = true;
        }
        else {
            toggles[i].checked = false;
        }
    }
}


async function submitChoices(event) {
    const formData = {
        world: document.getElementById("world_toggle").value,
        business: document.getElementById("business_toggle").value,
        technology: document.getElementById("technology_toggle").value,
        entertainment: document.getElementById("entertainment_toggle").value,
    };
    try {
        const response = await fetch("/settings", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(formData),
        });

        const data = await response.json();
        
        if(data.success) {
            alert("Changed settings successful")
        } else {
            alert("An error occured changing settings");
        }
    } catch(error) {
        alert("An error occured changing settings: " + data.error);
    }

}

document.addEventListener("DOMContentLoaded", setCheckValues);
document.getElementById("category_settings").addEventListener("submit", submitChoices);
