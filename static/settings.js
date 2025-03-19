//Just simple tabs code
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

//Gets already set stuff from database and checks the right boxes 
async function setCheckValues() {
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
        business.checked = data.business;
        technology.checked = data.technology;
        entertainment.checked = data.entertainment;
    }
    catch (error) {
        alert("An error occured fetching previous settings " + error);
    }
}

//Comment seems a bit redundant here 
async function submitChoices(event) {
    event.preventDefault();
    const formData = {
        business: document.getElementById("business_toggle").checked,
        technology: document.getElementById("technology_toggle").checked,
        entertainment: document.getElementById("entertainment_toggle").checked,
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
        } else {
            alert("An error occured changing settings: " + data.error);
        }
    } catch(error) {
        alert("An error occured changing settings: " + error);
    }

}

//Attaching functions to correct events
document.addEventListener("DOMContentLoaded", setCheckValues);
document.getElementById("category_settings").addEventListener("submit", submitChoices);
