jq(document).ready(function() {
  jq("#browsermessage #ignore").click(function() {
    jq.get('browsermessage_ignore', {}, function() {
      jq('#browsermessage').remove();
      jq('#browsermessage-overlay').remove();
    });
    return false;
  });
});