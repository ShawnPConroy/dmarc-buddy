<?php

/*
    Confirm requested file is legal: in a public folder and an XML file.
    Typicall passed `realpath($_SERVER['PATH_TRANSLATED'])`
    
    Adapted from https://github.com/ShawnPConroy/Nacms
    Which was adapted from https://github.com/sminnee/markdown-handler
*/
function is_legal_request($filePath, $ext) {
    $fileInfo = pathinfo($filePath);
    $legalExtension = strtolower($fileInfo['extension']) == strtolower($ext);

    // If OS name includes 'WIN' then replace backslashes with forwardslashes
    if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
        $documentRoot = str_replace('/', '\\', $_SERVER['DOCUMENT_ROOT']);
    } else {
        $documentRoot = $_SERVER['DOCUMENT_ROOT'];
    }
    
    $legalFolder = substr($filePath, 0, strlen($_SERVER['DOCUMENT_ROOT'])) == $documentRoot;
    return $filePath && $legalExtension && $legalFolder;
}