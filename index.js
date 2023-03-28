
var checked_categories = [];
var search_value = "";
var sort_value = "";

function load_XML_doc(path, show_content_func) {
    var BASEURL = "http://127.0.0.1:5000"
    var xmlhttp = new XMLHttpRequest();

    xmlhttp.onreadystatechange = function() {
        if (xmlhttp.readyState == XMLHttpRequest.DONE) {   // XMLHttpRequest.DONE == 4
           if (xmlhttp.status == 200) {
            show_content_func(xmlhttp.responseText)
           }
           else if (xmlhttp.status == 400) {
              alert('There was an error 400');
           }
           else {
               alert('something else other than 200 was returned: '+ xmlhttp.status);
               
           }
        }
    };
    document.getElementById("search_string").innerHTML = path;
    xmlhttp.open("GET", BASEURL+path, true);
    xmlhttp.send();
}

function show_content(content) {
    
    var json_content = JSON.parse(content).data;
    dest_div = document.getElementById("myArticle");
    dest_div.innerHTML = "";
    for (let i = 0; i < json_content.text.length; i++) {
        const temp_text = json_content.text[i];
        const temp_link_to_text = json_content.link_to_text[i];
        const last_changed = json_content.last_changed[i];
        
        
        let temp_box = document.createElement("div");
        let temp_headline = document.createElement("h2");
        let temp_box_under_head = document.createElement("div");
        temp_box.classList.add("dynamic_input")
        temp_box_under_head.classList.add("under_head_line");
        temp_box_under_head.innerHTML = "Letzte Änderung am: " + last_changed;

        // temp_headline.setAttribute("onclick", "accordion_function(this)");
        // temp_headline.classList.toggle("accordion");
        let temp_element = document.createElement("p");
        temp_element.classList.add("loaded_content");
        // temp_element.classList.toggle("panel");
        console.log(Date.parse(last_changed))
        
        temp_headline.innerHTML = temp_link_to_text;
        temp_element.innerHTML = temp_text;
        
        temp_box.appendChild(temp_headline);
        temp_box.appendChild(temp_box_under_head);
        temp_box.appendChild(temp_element);
        dest_div.appendChild(temp_box);

    }
}

function show_sport_categorie(content) {
    
    var json_content = JSON.parse(content).data;
    dest_div = document.getElementById("sports_categorie");
    for (let i = 0; i < json_content.length; i++) {
        const temp_sports_categorie = json_content[i];
        
        
        let temp_label = document.createElement("label");
        let temp_input = document.createElement("input");
        temp_input.type = 'checkbox';
        temp_input.setAttribute("onchange", "load_on_change(event)");

        temp_label.appendChild(temp_input);
        temp_label.innerHTML = temp_label.innerHTML + temp_sports_categorie;
        dest_div.appendChild(temp_label);

    }
}
load_XML_doc("/sports_categorie", show_sport_categorie);
// load_XML_doc("/sports"+search_value+"?sports_categories=" + checked_categories.join("&sports_categories="), show_content);


function load_on_change(e) {
    // console.log(e.target.parentElement.textContent +" "+e.target.checked);
    if(e.target.checked){
        checked_categories.push(e.target.parentElement.textContent)
    }
    else{
        checked_categories = checked_categories.filter(word => word != e.target.parentElement.textContent );
    }
    load_XML_doc("/sports"+search_value+"?sports_categories="+ checked_categories.join("&sports_categories=")+sort_value, show_content);
    
}
function on_sort_change(e) {
    console.log(e.target.value);
    sort_value = "&sort_value=" + e.target.value;
    load_XML_doc("/sports"+search_value+"?sports_categories="+ checked_categories.join("&sports_categories=")+sort_value, show_content);
}

function on_search_box_change(e) {
    search_value = e.target.value;
    if(search_value.length != 0)
    { 
        search_value = "/" + search_value;
    }else{
        // not sure if needed
        search_value = "";
    }

    load_XML_doc("/sports"+search_value+"?sports_categories="+ checked_categories.join("&sports_categories=")+sort_value, show_content);
}

function sports_with_para(e) {
    e.preventDefault();
    console.log(e);
    search_value = e.target[0].value;
    if(search_value.length != 0)
    { 
        search_value = "/" + search_value;
    }else{
        // not sure if needed
        search_value = "";
    }
    console.log(e);

    load_XML_doc("/sports"+search_value+"?sports_categories="+ checked_categories.join("&sports_categories=")+sort_value, show_content);
}