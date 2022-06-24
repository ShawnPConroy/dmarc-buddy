<?php
require_once("functions.php");

$filePath = realpath($_SERVER['PATH_TRANSLATED']);

if ( is_legal_request($filePath, 'xml') ) {
  header ("Content-Type:text/xml");
  $file = fopen($filePath,'r');
  $tableContent = '';
  while ($line = fgets($file)) {
    echo($line);
    if (substr($line, 0, 6) == "<?xml ") {
      echo("<?xml-stylesheet href=\"../css/xml.css\" type=\"text/css\"?>\n");
    }
  }
} else {
  echo("<p>DMARC-Buddy error: permission denied.</p>");
}