<?php

require_once("functions.php");

define("DATE_RECIEVED", 0);
define("DATE_START", 1);
define("DATE_END", 2);
define("REPORT_ORG", 3);
define("REPORT_ID", 4);
define("COUNT", 5);
define("SPF_EVAL", 6);
define("SPF_RESULT", 7);
define("DKIM_EVAL", 8);
define("DKIM_RESULT", 9);
define("SOURCE_IP", 10);
define("SOURCE_IP_LOOKUP", 11);
define("ENVELOPE_FROM", 12);
define("HEADER_FROM", 13);
define("SPF_DOMAIN", 14);
define("DKIM_DOMAIN", 15);
define("REPORT_FILENAME", 16);

$dataUrl = 'reports';
$filePath = realpath($_SERVER['PATH_TRANSLATED']);

/* Generate content */
if (is_legal_request($filePath, 'log')) {
  $fileInfo = pathinfo($filePath);
  $summaryDate = substr($fileInfo['filename'], 0, 7);
  $domainName = substr($fileInfo['filename'], 8);
  
  $weekPass = $weekFail = $monthPass = $monthFail = $lastMonthPass = $lastMonthFail = 0;
  $recordNum = 0;
  $domainLog = fopen($filePath,'r');
  while ($line = fgets($domainLog)) {
    $data = explode("\t", $line);

    $report = 
              'Recieved: ' . $data[DATE_RECIEVED] . '<br/>' . 
              'Start: ' . $data[DATE_START]. '<br/>' . 
              '  End: ' . $data[DATE_END] . '<br/>' . 
              'By: ' . $data[REPORT_ORG] . '<br/>' .
              'ID: <a href="../'.$dataUrl.'/' . $data[REPORT_FILENAME] . '">' . $data[REPORT_ID] . '</a><br/>';
    $count = $data[COUNT];

    $result = '<strong>SPF results</strong>:<br/>'.
              $data[SPF_EVAL] . ' ' . $data[SPF_RESULT].
              '<br/><strong>DMARC results</strong>:<br/>'.
              $data[DKIM_EVAL] . ' ' . $data[DKIM_RESULT];

    if (  strcmp($data[SPF_EVAL], "pass") || strcmp($data[SPF_RESULT], "pass") ||
          strcmp($data[DKIM_EVAL], "pass") || strcmp($data[DKIM_RESULT], "pass") ) {
      $resultClass = 'class="dmarcWarning"';
    }
    else {
      $resultClass = '';
    }
    
    $domains = '<br/>';
    if (!empty($data[ENVELOPE_FROM])) $domains .= 'Envelope From: '.$data[ENVELOPE_FROM].'<br/>';
    if (!empty($data[HEADER_FROM])) $domains .= 'Header From: '.$data[HEADER_FROM].'<br/>';
    if (!empty($data[SPF_DOMAIN])) $domains .= 'SPF: '.$data[SPF_DOMAIN].'<br/>';
    if (!empty($data[DKIM_DOMAIN])) $domains .= 'DMARC: '.$data[DKIM_DOMAIN];
    
    /* Skipping reverse lookup which sucks */
    $sources = 'Sending IP: <a href="https://mxtoolbox.com/SuperTool.aspx?action=ptr:'.
                $data[SOURCE_IP].'">'.$data[SOURCE_IP].'</a> '.$domains.'<br/>';

    $records[substr($data[DATE_RECIEVED],0,10)][$data[DATE_RECIEVED].$recordNum++] = [
      'statusClass' => $resultClass,
      'report' => $report,
      'count' => $count,
      'result' => $result,
      'sources' => $sources,
    ];

  }
  fclose($domainLog);

  krsort($records);
  $monthlyJson = file_get_contents($fileInfo['dirname'].'/'.$summaryDate.'-monthly.json');
  $stats = json_decode($monthlyJson, true);

  $monthPass = 991;
  $last7pass = $stats[$domainName]['pass']['last7'];
  $last7fail = $stats[$domainName]['fail']['last7'];
  $last28pass = $stats[$domainName]['pass']['last28'];
  $last28fail = $stats[$domainName]['fail']['last28'];
  $monthFail = 992;
  $weekPass = 993;
  $weekFail = 994;

  $weekIndicators = '';
  for($i=0; $i<=7; $i++) {
    if ($stats[$domainName]['fail'][$i] == 0 && $stats[$domainName]['pass'][$i] > 0) {
      // No fails, at least one pass
      $weekIndicators .= ' 🟩'; // large green square
    }
    else if ($stats[$domainName]['fail'][$i] > 0) {
      // Some fails
      $weekIndicators .= ' 🟥'; // large red square
    }
    else {
      // No reprots
      $weekIndicators .= ' ◻️'; // white medium square
    }
  }
  
  include("../views/log-view.php");
} else {
  echo("<p>DMARC-Buddy error: permission denied.</p>");
}
