function popupPreview(url, size1, size2) {
  size1 = size1 + 50;
  if (size1 > 850) {
    size1 = 850;
  }
  size2 = size2 + 150;
  if (size2 > 650) {
    size2 = 650;
  };
  w = window.open(url,"Popup","resizable=1,status=0,scrollbars=1,width=" + size1 +",height="+ size2 );
  w.focus();
}
