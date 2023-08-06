<?php
/*
    document2xhtml.php, PHP functions for aiding ODF=>XHTML transformations
    Copyright (C) 2003-2006 Arend van Beelen jr., Auton Rijnsburg
                            <arend@auton.nl>

    This library is free software; you can redistribute it and/or
    modify it under the terms of the GNU Lesser General Public
    License as published by the Free Software Foundation; either
    version 2.1 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public
    License along with this library; if not, write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
*/

class OpenDocument2XHTML
{
	public static function init($xslOptions)
	{
		self::$styles = array();
		self::$fontFaces = array();
		self::$listStyles = array();

		self::$xslOptions = $xslOptions;
	}

	public static function setFontFace($name, $family)
	{
		self::$fontFaces[$name] = $family;

		return '';
	}

	public static function fontFaceFamily($name)
	{
		return (isset(self::$fontFaces[$name]) ? self::$fontFaces[$name] : '');
	}

	public static function createStyle($family, $styleName, $parentStyleName = '')
	{
		if(isset(self::$styles[$family]) == false)
		{
			self::$styles[$family] = array();
		}
		if(isset(self::$styles[$family][$styleName]) == false)
		{
			if(isset(self::$styles[$family][$parentStyleName]))
			{
				self::$styles[$family][$styleName] = self::$styles[$family][$parentStyleName];
			}
			else
			{
				self::$styles[$family][$styleName] = array();
			}
		}

		return '';
	}

	public static function createListStyle($styleName)
	{
		if(isset(self::$listStyles[$styleName]) == false)
		{
			self::$listStyles[$styleName] = array();
		}

		return '';
	}

	public static function setStyleTextProperties($family,
	                                              $styleName,
	                                              $fontName,
	                                              $fontSize,
	                                              $fontStyle,
	                                              $fontWeight,
	                                              $textUnderlineStyle,
	                                              $color,
	                                              $backgroundColor,
	                                              $textPosition)
	{
		self::createStyle($family, $styleName);

		self::$styles[$family][$styleName] = array_merge(self::$styles[$family][$styleName],
		                                                 self::cssStyleTextProperties($fontName,
		                                                                              $fontSize,
		                                                                              $fontStyle,
		                                                                              $fontWeight,
		                                                                              $textUnderlineStyle,
		                                                                              $color,
		                                                                              $backgroundColor,
		                                                                              $textPosition));

		return '';
	}

	public static function setStyleParagraphProperties($family,
	                                                   $styleName,
	                                                   $marginTop,
	                                                   $marginRight,
	                                                   $marginBottom,
	                                                   $marginLeft,
	                                                   $textIndent,
	                                                   $textAlign)
	{
		self::createStyle($family, $styleName);

		self::$styles[$family][$styleName] = array_merge(self::$styles[$family][$styleName],
		                                                 self::cssStyleParagraphProperties($marginTop,
		                                                                                   $marginRight,
		                                                                                   $marginBottom,
		                                                                                   $marginLeft,
		                                                                                   $textIndent,
		                                                                                   $textAlign));

		return '';
	}

	public static function setStyleTableProperties($family,
	                                               $styleName,
	                                               $width)
	{
		self::createStyle($family, $styleName);

		self::$styles[$family][$styleName] = array_merge(self::$styles[$family][$styleName],
		                                                 self::cssStyleTableProperties($width));

		return '';
	}

	public static function setStyleTableColumnProperties($family,
	                                                     $styleName,
	                                                     $columnWidth)
	{
		self::createStyle($family, $styleName);

		self::$styles[$family][$styleName] = array_merge(self::$styles[$family][$styleName],
		                                                 self::cssStyleTableColumnProperties($columnWidth));

		return '';
	}

	public static function setStyleTableRowProperties($family,
	                                                  $styleName,
	                                                  $rowHeight)
	{
		self::createStyle($family, $styleName);

		self::$styles[$family][$styleName] = array_merge(self::$styles[$family][$styleName],
		                                                 self::cssStyleTableRowProperties($rowHeight));

		return '';
	}

	public static function setStyleTableCellProperties($family,
	                                                   $styleName,
	                                                   $margin,
	                                                   $marginTop,
	                                                   $marginRight,
	                                                   $marginBottom,
	                                                   $marginLeft,
	                                                   $padding,
	                                                   $paddingTop,
	                                                   $paddingRight,
	                                                   $paddingBottom,
	                                                   $paddingLeft,
	                                                   $border,
	                                                   $borderTop,
	                                                   $borderRight,
	                                                   $borderBottom,
	                                                   $borderLeft,
	                                                   $backgroundColor)
	{
		self::createStyle($family, $styleName);

		self::$styles[$family][$styleName] = array_merge(self::$styles[$family][$styleName],
		                                                 self::cssStyleTableCellProperties($margin,
		                                                                                   $marginTop,
		                                                                                   $marginRight,
		                                                                                   $marginBottom,
		                                                                                   $marginLeft,
		                                                                                   $padding,
		                                                                                   $paddingTop,
		                                                                                   $paddingRight,
		                                                                                   $paddingBottom,
		                                                                                   $paddingLeft,
		                                                                                   $border,
		                                                                                   $borderTop,
		                                                                                   $borderRight,
		                                                                                   $borderBottom,
		                                                                                   $borderLeft,
		                                                                                   $backgroundColor));

		return '';
	}

	public static function setStyleListProperties($styleName,
	                                              $listLevel,
	                                              $bulletChar,
	                                              $numFormat,
	                                              $spaceBefore,
	                                              $minLabelWidth)
	{
		self::createListStyle($styleName);

		self::$listStyles[$styleName][$listLevel] = self::cssStyleListProperties($bulletChar,
		                                                                         $numFormat,
		                                                                         $spaceBefore,
		                                                                         $minLabelWidth);

		return '';
	}

	public static function setStyleGraphicProperties($family,
	                                                 $styleName,
	                                                 $wrap,
	                                                 $verticalPos,
	                                                 $horizontalPos)
	{
		self::createStyle($family, $styleName);

		self::$styles[$family][$styleName] = array_merge(self::$styles[$family][$styleName],
		                                                 self::cssStyleGraphicProperties($wrap,
		                                                                                 $verticalPos,
		                                                                                 $horizontalPos));

		return '';
	}

	public static function style($family, $styleName, $onlyProperties = '')
	{
		$styleArray = (isset(self::$styles[$family][$styleName]) ? self::$styles[$family][$styleName] :
		               (isset(self::$styles[$family]['']) ? self::$styles[$family][''] : array()));

		$style = '';
		$onlyProperties = ($onlyProperties == '' ? false : explode(',', $onlyProperties));
		foreach($styleArray as $key => $value)
		{
			if($onlyProperties !== false &&
			   in_array($key, $onlyProperties) == false)
			{
				continue;
			}
			if($style != '')
			{
				$style .= '; ';
			}
			$style .= "$key: $value";
		}

		return $style;
	}

	public static function listStyle($styleName, $listLevel, $onlyProperties = '')
	{
		$styleArray = (isset(self::$listStyles[$styleName][$listLevel]) ?
		               self::$listStyles[$styleName][$listLevel] : array());

		$style = '';
		$onlyProperties = ($onlyProperties == '' ? false : explode(',', $onlyProperties));
		foreach($styleArray as $key => $value)
		{
			if($onlyProperties !== false &&
			   in_array($key, $onlyProperties) == false)
			{
				continue;
			}
			if($style != '')
			{
				$style .= '; ';
			}
			$style .= "$key: $value";
		}

		return $style;
	}

	private static function cssStyleTextProperties($fontName,
	                                               $fontSize,
	                                               $fontStyle,
	                                               $fontWeight,
	                                               $textUnderlineStyle,
	                                               $color,
	                                               $backgroundColor,
	                                               $textPosition)
	{
		$style = array();

		if(isset(self::$xslOptions['ignore-font-name-and-size']) == true &&
		   self::$xslOptions['ignore-font-name-and-size'] == 'true')
		{
			if($fontName != '')
			{
				$font = self::fontFaceFamily($fontName);
				if(strpos($font, 'Courier') !== false ||
				   strpos($font, 'Cumberland') !== false)
				{
					$style['font-family'] = 'Courier New';
				}
			}
		}
		else
		{
			if($fontName != '')
			{
				$style['font-family'] = self::fontFaceFamily($fontName);
			}
			if($fontSize != '')
			{
				$style['font-size'] = $fontSize;
			}
		}
		if($fontStyle != '')
		{
			$style['font-style'] = $fontStyle;
		}
		if($fontWeight != '')
		{
			$style['font-weight'] = $fontWeight;
		}
		if($textUnderlineStyle != '')
		{
			$style['text-decoration'] = 'underline';
		}
		if($color != '')
		{
			$style['color'] = $color;
		}
		if($backgroundColor != '')
		{
			$style['background-color'] = $backgroundColor;
		}
		if($textPosition != '')
		{
			if(strpos($textPosition, ' ') !== false)
			{
				list($verticalPos, $fontHeight) = explode(' ', $textPosition);
			}
			else
			{
				$verticalPos = $textPosition;
				$fontHeight = '';
			}

			$style['vertical-align'] = $verticalPos;
			if($fontHeight != '')
			{
				$style['font-size'] = $fontHeight;
			}
		}

		return $style;
	}

	private static function cssStyleParagraphProperties($marginTop,
	                                                    $marginRight,
	                                                    $marginBottom,
	                                                    $marginLeft,
	                                                    $textIndent,
	                                                    $textAlign)
	{
		$style = array();

		if($marginTop != '')
		{
			$style['margin-top'] = $marginTop;
		}
		if($marginRight != '')
		{
			$style['margin-right'] = $marginRight;
		}
		if($marginBottom != '')
		{
			$style['margin-bottom'] = $marginBottom;
		}
		if($marginLeft != '')
		{
			$style['margin-left'] = $marginLeft;
		}
		if($textIndent != '')
		{
			$style['text-indent'] = $textIndent;
		}
		if($textAlign != '')
		{
			$style['text-align'] = ($textAlign == 'start'  || $textAlign == 'left'  ? 'left' :
			                       ($textAlign == 'center'                          ? 'center' :
			                       ($textAlign == 'end'    || $textAlign == 'right' ? 'right' :
			                       ($textAlign == 'justify'                         ? 'justify' :
			                       ('')))));
		}

		return $style;
	}

	private static function cssStyleTableProperties($width)
	{
		$style = array();

		if($width != '')
		{
			$style['width'] = $width;
		}

		return $style;
	}

	private static function cssStyleTableColumnProperties($columnWidth)
	{
		$style = array();

		if($columnWidth != '')
		{
			$style['width'] = $columnWidth;
		}

		return $style;
	}

	private static function cssStyleTableRowProperties($rowHeight)
	{
		$style = array();

		if($rowHeight != '')
		{
			$style['height'] = $rowHeight;
		}

		return $style;
	}

	private static function cssStyleTableCellProperties($margin,
	                                                    $marginTop,
	                                                    $marginRight,
	                                                    $marginBottom,
	                                                    $marginLeft,
	                                                    $padding,
	                                                    $paddingTop,
	                                                    $paddingRight,
	                                                    $paddingBottom,
	                                                    $paddingLeft,
	                                                    $border,
	                                                    $borderTop,
	                                                    $borderRight,
	                                                    $borderBottom,
	                                                    $borderLeft,
	                                                    $backgroundColor)
	{
		$style = array();

		if($margin != '')
		{
			$style['margin'] = $margin;
		}
		if($marginTop != '')
		{
			$style['margin-top'] = $marginTop;
		}
		if($marginRight != '')
		{
			$style['margin-right'] = $marginRight;
		}
		if($marginBottom != '')
		{
			$style['margin-bottom'] = $marginBottom;
		}
		if($marginLeft != '')
		{
			$style['margin-left'] = $marginLeft;
		}

		if($padding != '')
		{
			$style['padding'] = $padding;
		}
		if($paddingTop != '')
		{
			$style['padding-top'] = $paddingTop;
		}
		if($paddingRight != '')
		{
			$style['padding-right'] = $paddingRight;
		}
		if($paddingBottom != '')
		{
			$style['padding-bottom'] = $paddingBottom;
		}
		if($paddingLeft != '')
		{
			$style['padding-left'] = $paddingLeft;
		}

		if(isset(self::$xslOptions['ignore-cell-border-properties']) == false ||
		   self::$xslOptions['ignore-cell-border-properties'] != 'true')
		{
			if($border != '')
			{
				$style['border'] = self::replaceBorderThickness($border);
			}
			if($borderTop != '')
			{
				$style['border-top'] = self::replaceBorderThickness($borderTop);
			}
			if($borderRight != '')
			{
				$style['border-right'] = self::replaceBorderThickness($borderRight);
			}
			if($borderBottom != '')
			{
				$style['border-bottom'] = self::replaceBorderThickness($borderBottom);
			}
			if($borderLeft != '')
			{
				$style['border-left'] = self::replaceBorderThickness($borderLeft);
			}
		}

		if($backgroundColor != '')
		{
			$style['background-color'] = $backgroundColor;
		}

		return $style;
	}

	private static function cssStyleListProperties($bulletChar,
	                                               $numFormat,
	                                               $spaceBefore,
	                                               $minLabelWidth)
	{
		$style = array();

		if((isset(self::$xslOptions['ignore-list-properties']) == false ||
		    self::$xslOptions['ignore-list-properties'] != 'true') &&
		   $bulletChar != '')
		{
			if($spaceBefore != '')
			{
				$style['margin-left'] = $spaceBefore;
			}
			if($minLabelWidth != '')
			{
				$style['min-width'] = $minLabelWidth;
			}
			if($spaceBefore != '' || $minLabelWidth != '')
			{
				$unit = 'cm';
				if(substr($spaceBefore, -2) == 'in')
				{
					$unit = 'in';
				}
				$style['total-width'] = ($spaceBefore + $minLabelWidth).$unit;
			}
			if($bulletChar != '')
			{
				$style['list-style-type'] = "custom $bulletChar";
			}
		}

		if($bulletChar == '')
		{
			if($numFormat == '1')
			{
				$style['list-style-type'] = 'decimal';
			}
			elseif($numFormat == 'a')
			{
				$style['list-style-type'] = 'lower-alpha';
			}
			elseif($numFormat == 'A')
			{
				$style['list-style-type'] = 'upper-alpha';
			}
			elseif($numFormat == 'i')
			{
				$style['list-style-type'] = 'lower-roman';
			}
			elseif($numFormat == 'I')
			{
				$style['list-style-type'] = 'upper-roman';
			}
		}

		return $style;
	}

	private static function cssStyleGraphicProperties($wrap,
	                                                  $verticalPos,
	                                                  $horizontalPos)
	{
		$style = array();

		if($verticalPos == 'top' ||
		   $verticalPos == 'middle' ||
		   $verticalPos == 'bottom')
		{
			$style['vertical-align'] = $verticalPos;
		}
		if($horizontalPos == 'left' ||
		   $horizontalPos == 'center' ||
		   $horizontalPos == 'right')
		{
			$style['text-align'] = $horizontalPos;
		}

		return $style;
	}

	private static function replaceBorderThickness($border)
	{
		$thickness = (strpos($border, 'double') === false ? '1px' : '3px');
		$border = preg_replace(array('/\d+\.\d+cm/',
		                             '/\d+\.\d+in/'), $thickness, $border);
		return $border;
	}

	private static $styles;
	private static $fontFaces;
	private static $listStyles;

	private static $xslOptions;
}

?>
