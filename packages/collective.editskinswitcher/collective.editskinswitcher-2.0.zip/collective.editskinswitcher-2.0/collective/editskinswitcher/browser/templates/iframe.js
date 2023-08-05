// stretch the preview iframe to fit the edit interface

function calcHeight()
{
  iframe = document.getElementById('editskinswitcher-preview');
  iframe.height=iframe.contentWindow.document.body.scrollHeight;
}
