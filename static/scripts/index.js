
// sports_categories
var checked_categories = [];
if(document.getElementById("sports_categories").innerText.length != 0){
    checked_categories = JSON.parse(document.getElementById("sports_categories").innerText);
}

// serach_value
var search_value = document.getElementById("sport_name").innerHTML;
var sort_value = document.getElementById("sort_value").innerHTML;

// document.getElementById("search_string").innerHTML = "/sports"+search_value_for_url,"?sports_categories="+ checked_categories_for_url.join("&sports_categories=")+"&sort_value="+sort_value_for_url;

var search_form_visibility = "block";

function create_url_save_parameter(search_value, sort_value, checked_categories) {
    search_value_for_url = encodeURIComponent(search_value)
    sort_value_for_url = encodeURIComponent(sort_value)
    checked_categories_for_url = []
    for (let i = 0; i < checked_categories.length; i++) {
        const element = checked_categories[i];
        checked_categories_for_url.push(encodeURIComponent(element))
        
    }
    console.log({"search_value":search_value_for_url,"sort_value":sort_value_for_url,"checked_categories":checked_categories_for_url});
    return {"search_value":search_value_for_url,"sort_value":sort_value_for_url,"checked_categories":checked_categories_for_url};
}




function disable_useless_categories(useful_categories) {
    useful_categories = JSON.parse(useful_categories);
    if(useful_categories.length != 0){
        categories = document.getElementById("sports_categorie").querySelectorAll("label:not([checked])");
        for (let i = 0; i < categories.length; i++) {
            const element = categories[i];
            if(useful_categories.filter(category => category.includes(element.textContent)).length == 0){
                element.firstChild.setAttribute("disabled", "");
            }else{
                element.firstChild.removeAttribute("disabled");
            }
            
        }
    }
    else{
        categories = document.getElementById("sports_categorie").querySelectorAll("input[disabled]");
        if(categories != null){
            for (let i = 0; i < categories.length; i++) {
                const element = categories[i];
                element.removeAttribute("disabled");
            }
        }

    }
}
function change_description_tag(new_description) {
    document
      .getElementsByTagName('meta')
      .namedItem('description')
      .setAttribute('content',new_description)
}

function load_XML_doc(path, params , show_content_func) {
    var BASEURL = "http://127.0.0.1:5000"
    var xmlhttp = new XMLHttpRequest();

    xmlhttp.onreadystatechange = function() {
        if (xmlhttp.readyState == XMLHttpRequest.DONE) {   // XMLHttpRequest.DONE == 4
           if (xmlhttp.status == 200) {

            var json_content = JSON.parse(xmlhttp.responseText);    
            show_content_func(json_content.data);

            if(path == "/sports_categorie"){
                // only load setup
                setup()
                
            }else{
                // only set history for serach results!
                window.history.pushState({}, '',BASEURL + path.replace("sports", "index") + params);
                
                document.getElementById("search_string").innerHTML = path + params;
                disable_useless_categories(json_content.categorie_can_used)
                change_description_tag(json_content.new_description)
            }
            
            
           }
           else if (xmlhttp.status == 400) {
              alert('There was an error 400');
           }
           else {
               alert('something else other than 200 was returned: '+ xmlhttp.status);
           }
        }
    };

    xmlhttp.open("GET", BASEURL + path + params, true);
    xmlhttp.setRequestHeader("Content-type","application/json");
    xmlhttp.send(params);
}

function show_content_precreated_html(html_result) {
    // console.log(html_result);
    dest_div = document.getElementById("myArticle").innerHTML = html_result;
    // dest_div.appendChild(html_result)
}


function show_content(json_content) {

    dest_div = document.getElementById("myArticle");
    dest_div.innerHTML = "";
    for (let i = 0; i < json_content.length; i++) {

        const temp_text = json_content[i].piped_text;
        // const temp_text = json_content[i].text;
        const temp_link_to_text = json_content[i].link_to_text;
        const last_changed = json_content[i].last_changed;
        
        
        let temp_box = document.createElement("div");
        temp_box.id = temp_link_to_text;
        let temp_headline = document.createElement("h2");
        temp_headline.classList.add("headline_of_content");
        let temp_box_under_head = document.createElement("div");
        temp_box.classList.add("dynamic_input")
        temp_box_under_head.classList.add("under_head_line");
        temp_box_under_head.innerHTML = "Letzte Änderung am: " + last_changed;

        // temp_headline.setAttribute("onclick", "accordion_function(this)");
        // temp_headline.classList.toggle("accordion");
        let temp_element = document.createElement("p");
        temp_element.classList.add("loaded_content");
        // temp_element.classList.toggle("panel");
        
        temp_headline.innerHTML = temp_link_to_text;
        temp_element.innerHTML = temp_text;
        
        temp_box.appendChild(temp_headline);
        temp_box.appendChild(temp_box_under_head);
        temp_box.appendChild(temp_element);
        dest_div.appendChild(temp_box);
        if(i == 0){
        document.location.hash = "";
        document.location.hash = temp_link_to_text; 
        // document.querySelector("#myArticle:first-child").id;
        }
    }
}

function show_sport_categorie(json_content) {
    
    dest_div = document.getElementById("sports_categorie");
    for (let i = 0; i < json_content.length; i++) {

        const temp_sports_categorie = json_content[i];
        let temp_label = document.createElement("label");
        let temp_input = document.createElement("input");
        temp_input.classList.add("category_class");
        temp_input.type = 'checkbox';
        temp_input.setAttribute("onchange", "load_on_change(event)");

        temp_label.appendChild(temp_input);
        temp_label.innerHTML = temp_label.innerHTML + temp_sports_categorie;
        dest_div.appendChild(temp_label);
    }
}
// load_XML_doc("/sports"+search_value+"?sports_categories=" + checked_categories.join("&sports_categories="), show_content);


function load_on_change(e) {
    // console.log(e.target.parentElement.textContent +" "+e.target.checked);
    checked_categories = checked_categories.filter(word => word != "");

    if(e.target.checked){
        checked_categories.push(e.target.parentElement.textContent)
        console.log(e.target.parentElement.textContent);
    }
    else{
        checked_categories = checked_categories.filter(word => word != e.target.parentElement.textContent);
    }

    url_save_params = create_url_save_parameter(search_value, sort_value, checked_categories);
    console.log(url_save_params["search_value"]);
    load_XML_doc("/sports"+url_save_params["search_value"],"?sports_categories="+ url_save_params["checked_categories"].join("&sports_categories=")+"&sort_value="+url_save_params["sort_value"], show_content_precreated_html);
    
}
function on_sort_change(e) {
    sort_value = e.target.value;
    
    url_save_params = create_url_save_parameter(search_value, sort_value, checked_categories);
    console.log(url_save_params["search_value"]);
    load_XML_doc("/sports"+url_save_params["search_value"],"?sports_categories="+ url_save_params["checked_categories"].join("&sports_categories=")+"&sort_value="+url_save_params["sort_value"], show_content_precreated_html);
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

    url_save_params = create_url_save_parameter(search_value, sort_value, checked_categories);
    console.log(url_save_params["search_value"]);
    load_XML_doc("/sports"+url_save_params["search_value"],"?sports_categories="+ url_save_params["checked_categories"].join("&sports_categories=")+"&sort_value="+url_save_params["sort_value"], show_content_precreated_html);}

function sports_with_para(e) {
    // e.preventDefault();
    search_value = e.target[0].value;
    if(search_value.length != 0)
    { 
        search_value = "/" + search_value;
    }else{
        // not sure if needed
        search_value = "";
    }

    url_save_params = create_url_save_parameter(search_value, sort_value, checked_categories);
    console.log(url_save_params["search_value"]);
    load_XML_doc("/sports"+url_save_params["search_value"],"?sports_categories="+ url_save_params["checked_categories"].join("&sports_categories=")+"&sort_value="+url_save_params["sort_value"], show_content_precreated_html);
    return false;
}

function toggle_serach_form() {
    if(search_form_visibility == "none"){
        search_form_visibility = "block";

        document.getElementById("opposite_of_serach_form").style.display = "none";

    }
    else{
        search_form_visibility = "none";
        document.getElementById("opposite_of_serach_form").style.display = "block";

    }
    document.getElementsByClassName("serach_form")[0].style.display = search_form_visibility;
}

const umlautMap = {
    '\u00dc': 'UE',
    '\u00c4': 'AE',
    '\u00d6': 'OE',
    '\u00fc': 'ue',
    '\u00e4': 'ae',
    '\u00f6': 'oe',
    '\u00df': 'ss',
  }
  
  function replaceUmlaute(str) {
    console.log(str);
    return str
      .replace(/[\u00dc|\u00c4|\u00d6][a-z]/g, (a) => {
        const big = umlautMap[a.slice(0, 1)];
        return big.charAt(0) + big.charAt(1).toLowerCase() + a.slice(1);
      })
      .replace(new RegExp('['+Object.keys(umlautMap).join('|')+']',"g"),
        (a) => umlautMap[a]
      );
  }



function subscribe_to_sport(event) {
    const link_to_text = event.target.parentElement.id;
    event.target.classList.toggle("loading_text");
    url = "https://t.me/test_21091998_bot?start="+replaceUmlaute(link_to_text.replace("index.php/","").replace(/[\W_]+/g,""));
    params = []

    var BASEURL = "http://127.0.0.1:5000"
    var xmlhttp = new XMLHttpRequest();

    xmlhttp.onreadystatechange = function() {
        if (xmlhttp.readyState == XMLHttpRequest.DONE) {   // XMLHttpRequest.DONE == 4
           if (xmlhttp.status == 200) {  
            console.log("span_"+link_to_text);      
            event.target.classList.toggle("loading_text");
            document.getElementById("span_"+link_to_text).innerHTML = xmlhttp.responseText;
           }
           else if (xmlhttp.status == 400) {
            event.target.classList.toggle("loading_text");  
            alert('There was an error 400');
              
           }
           else {
               event.target.classList.toggle("loading_text");
               alert('something else other than 200 was returned: '+ xmlhttp.status);
           }
        }
    };

    xmlhttp.open("GET", BASEURL + "/subscribe/" + encodeURIComponent(link_to_text), true);
    xmlhttp.setRequestHeader("Content-type","application/json");
    xmlhttp.send(params);
    window.open(url)
    // navigator.share({
    //     title: 'Subscribe to ' + link_to_text,
    //     text: 'You got 10 minutes to click on the start button!',
    //     url: url
    //    })

}


function setup() {

    if(sort_value.length != 0){
        // set sort with data from url
        decoded_url = decodeURIComponent(sort_value)
        Array.from(document.querySelectorAll("[name=sort]")).filter(d => d.value.includes(sort_value))[0].selected = "selected";      
    }


    if(search_value.length != 0)
    {
        // fill input with data from url
        decoded_url = decodeURIComponent(search_value.substring(1))
        document.getElementById("name").value = decoded_url;    
        // load_XML_doc("/sports"+search_value,"?sports_categories="+ checked_categories.join("&sports_categories=")+"&sort_value="+sort_value, show_content);
    }
    if(checked_categories.length != 0 && checked_categories[0].length != 0)
    {
        // set categories with data from url
        for (let i = 0; i < checked_categories.length; i++) {
            let element = checked_categories[i];
            
            element = decodeURIComponent(element)
            console.log(document.querySelectorAll("[type=checkbox]"));
            Array.from(document.querySelectorAll("[type=checkbox]")).filter(d => d.parentNode.innerText.includes(element))[0].checked = true;
        }
        // load_XML_doc("/sports"+search_value,"?sports_categories="+ checked_categories.join("&sports_categories=")+"&sort_value="+sort_value, show_content);

    }
    
}

// setup();
load_XML_doc("/sports_categorie","",show_sport_categorie);