function doPost(e) {
  // Parse JSON data from the POST request
  var postData = JSON.parse(e.postData.contents);

  // Create a UUID
  var uuid = Utilities.getUuid();

  // Get time
  var now = new Date();

  // Format the date as a string
  var formattedTime = Utilities.formatDate(now, "GMT+7", "yyyy-MM-dd HH:mm:ss");

  // Get the active sheet
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();

  // Add a new row with UUID, Name, Description, and Link
  sheet.appendRow([
    uuid,
    postData.name,
    postData.description,
    postData.tags,
    postData.link,
    postData.uploadedBy,
    formattedTime,
  ]);

  // Return success response
  return ContentService.createTextOutput("Row added successfully");
}
