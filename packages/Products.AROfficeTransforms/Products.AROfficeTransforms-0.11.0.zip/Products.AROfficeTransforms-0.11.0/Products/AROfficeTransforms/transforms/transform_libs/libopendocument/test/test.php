<?php

require_once('../interfaces/php5/OpenDocument.php');

$filename = (isset($_SERVER['argv'][1]) ? $_SERVER['argv'][1] : 'testfile');

$od = new OpenDocument();

$od->open("$filename.odt");
$od->setXSLTransformation('aukyla');
$od->setXSLOption('ignore-font-name-and-size', 'true');
$od->convertToXHTML("$filename.xhtml");
$od->close();

?>
