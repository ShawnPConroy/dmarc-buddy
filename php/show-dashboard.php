<?php 
$dataPath = '../data';
$dataUrl = 'data';

// Calculate dates
$monthsAgo[0] = new DateTime('first day of this month');
$monthsAgoName[0] = $monthsAgo[0]->format('F');
$monthsAgoId[0] = $monthsAgo[0] ->format('Y-m');

$monthsAgo[1] = new DateTime($monthsAgoId[0] . '-01 -1 month');
$monthsAgoName[1] = $monthsAgo[1]->format('F');
$monthsAgoId[1] = $monthsAgo[1] ->format('Y-m');

$monthsAgo[2] = new DateTime($monthsAgoId[0] . '-01 -2 months');
$monthsAgoName[2] = $monthsAgo[2]->format('F');
$monthsAgoId[2] = $monthsAgo[2] ->format('Y-m');

$monthsAgoFile[0] = $dataPath.'/'.$monthsAgoId[0].'-monthly.json';
$monthsAgoFile[1] = $dataPath.'/'.$monthsAgoId[1].'-monthly.json';
$monthsAgoFile[2] = $dataPath.'/'.$monthsAgoId[2].'-monthly.json';


function loadMonthly($file, $month, &$stats) {
  $domainList = array(); // To sort domains on dashboard
  for ($i=0; $i<=2; $i++){

    if (file_exists($file[$i])) {
      $monthlyJson = file_get_contents($file[$i]);
      $summary = json_decode($monthlyJson, true);
      foreach($summary as $domain => $data) {
        // Save each domain summary for month $i
        $stats[$domain][$month[$i]] = $data;
        
        // If $i==0 it's the real current month, move current emails to the top
        if ($i==0) {
          $domainList[$data['lastReport'].$domain] = $domain;
        }
        else if (!in_array($domain, $domainList)) {
          // Default to 9, which sorts at the bottom of any year
          // Will work until the 10th millenium
          $domainList['9'] = $domain;
        }
      }
    }
  }
  return $domainList;
}

$stats = array();

// Domain List will be missing domains with no report this month
$domainList = loadMonthly($monthsAgoFile, $monthsAgoId, $stats);
krsort($domainList);
include("../views/dashboard-view.php");