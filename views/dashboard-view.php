<!doctype html>

<head>
  <meta charset="utf-8">
  <title>DMARC Dashboard</title>
  <meta name="robots" content="noindex,nofollow">

    <link rel="apple-touch-icon" href="icon.png">
  <!-- Place favicon.ico in the root directory -->

  <link rel="stylesheet" href="css/dashboard.css">

</head>

<body>
  <header>
    <h1>DMARC Dashboard</h1>
  </header>
  <main>
<?php

function showMonthTotals($data, $domainName, $month, $monthsAgoId, $monthsAgoName, $dataUrl) {
  echo "\t\t<div class=\"monthlySummary\">";
  echo "<span class=\"month\"><a href=\"{$dataUrl}/{$monthsAgoId[$month]}-{$domainName}.log\">".$monthsAgoName[$month]."</a></span> ";
  $highlight = ($data['pass']['count'] != 0) ? "highlight" : '';
  echo "<span class=\"pass {$highlight}\"> {$data['pass']['count']} pass </span> ";
  $highlight = ($data['fail']['count'] != 0) ? "highlight" : '';
  echo "<span class=\"fail {$highlight}\"> {$data['fail']['count']} fail </span> ";
  echo "</div>\n";
}

function showDomain($domainName, $data, $monthsAgoId, $monthsAgoName, $dataUrl) {
  echo "\t<h2>Stats for $domainName</h2>\n\n";
  if (isset($data[$monthsAgoId['0']])) {
    echo "\t<p>Most recent report received at {$data[$monthsAgoId['0']]['lastReport']}</p>";
  }
  else {
    echo "\t<p>No reports for this month.</p>";
  }
  echo "\t<div class=\"weekStats\">\n";
  echo "\t\t<div class=\"dayStatsHeader\">Today &amp; past 7</a></div>\n";
  for($i=0; $i<=7; $i++) {
    if(isset($data[$monthsAgoId[0]])) {
      $pass = $data[$monthsAgoId[0]]['pass'][$i];
      $fail = $data[$monthsAgoId[0]]['fail'][$i];
    }
    else {
      $pass = 0;
      $fail = 0;
    }
    echo "<div class=\"dayStats\">";
    $highlight = ($pass != 0) ? "highlight" : '';
    echo "<span class=\"pass {$highlight}\">{$pass} pass </span>";
    $highlight = ($fail != 0) ? "highlight" : '';
    echo "<span class=\"fail {$highlight}\">{$fail} fail </span>";
    echo "</div>";
  }
  echo "\t</div>\n";
  
  echo "\t<footer>\n";

  $monthData = isset($data[$monthsAgoId[2]]) ? $data[$monthsAgoId[2]] : ['pass'=>['count'=>'0'], 'fail'=>['count'=>'0']];
  showMonthTotals($monthData, $domainName, 2, $monthsAgoId, $monthsAgoName, $dataUrl);
  $monthData = isset($data[$monthsAgoId[1]]) ? $data[$monthsAgoId[1]] : ['pass'=>['count'=>'0'], 'fail'=>['count'=>'0']];
  showMonthTotals($monthData, $domainName, 1, $monthsAgoId, $monthsAgoName, $dataUrl);
  $monthData = isset($data[$monthsAgoId[0]]) ? $data[$monthsAgoId[0]] : ['pass'=>['count'=>'0'], 'fail'=>['count'=>'0']];
  showMonthTotals($monthData, $domainName, 0, $monthsAgoId, $monthsAgoName, $dataUrl);
  
  echo "\t</footer>\n";
}

echo "\n\n<section class=\"allDomains\">\n";
showDomain('all', $stats['all'], $monthsAgoId, $monthsAgoName, $dataUrl);
echo "</section>\n\n";

foreach($domainList as $domainName) {
  echo "\n\n<section>\n";
  showDomain($domainName, $stats[$domainName], $monthsAgoId, $monthsAgoName, $dataUrl);
  echo "</section>\n\n";
}
?>
  </main>

  <footer>
    <p>Dashboard generated by DMARC-Buddy. Domains listed by most recently
      recieved DMARC report. Reports are typical sent with different delays
      by different reporting orgs (email service providers). For this reason
      all reports and records are shown grouped by date received.</p>
  </footer>
</body>

</html>
