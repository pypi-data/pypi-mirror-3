function showOrHide(elementName)
{
    var el = document.getElementById(elementName);
    if (el !== undefined)
    {
        if (el.style.display == 'none')
            el.style.display = '';
        else
            el.style.display = 'none';
    }
}
