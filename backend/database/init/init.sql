DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'gosts') THEN
        EXECUTE 'CREATE DATABASE gosts';
    END IF;
END
$$;

\c gosts;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'standarts') THEN
        CREATE TABLE standarts (
            id SERIAL PRIMARY KEY,
            standart_name VARCHAR(255) NOT NULL,
            standart_json JSONB NOT NULL,
            UNIQUE (standart_name)
        );
    END IF;
END
$$;

DO $$
DECLARE
    v_standart_name VARCHAR(255) := '7.32-2017';
    v_file_content JSONB := '
{
  "report_format": {
    "margins": {
      "left": "30mm",
      "right": "15mm",
      "top": "20mm",
      "bottom": "20mm",
      "paragraph_indent": "1.25cm"
    },
    "font": {
      "color": "black",
      "size": "12pt",
      "min_size": "12",
      "default_type": "Times New Roman",
      "type": "Times New Roman",
      "bold": {
        "apply_to": [
          "section_titles",
          "subsection_titles",
          "structural_element_titles"
        ]
      },
      "italic": {
        "apply_to": [
          "objects",
          "terms_in_latin"
        ]
      }
    },
    "page_numbering": {
      "style": "ARABIC",
      "position": [
        "Bottom",
        "Center"
      ],
      "starting_page": 2
    },
    "titles": {
      "position": "center",
      "capitalization": "all",
      "underline": false,
      "end_with_period": false,
      "sections_new_page": true,
      "sections_and_subsections": {
        "indent": "paragraph",
        "bold": true,
        "capitalize_first_letter": true,
        "underline": false,
        "end_with_period": false
      }
    },
    "illustrations": {
      "object_position": [
        "after_first_reference",
        "after_next_page"
      ],
      "reference_in_text": {
        "word": "рисунок",
        "number": true
      },
      "numbering": {
        "style": "ARABIC",
        "continuous": true,
        "per_section": true,
        "appendices": {
          "separate_numbering": true,
          "prefix": "{appendix_id}."
        }
      },
      "title_position": "center",
      "title_format": {
        "capitalize_first_letter": true,
        "end_with_period": false,
        "line_spacing": "1"
      }
    },
    "tables": {
      "object_position": [
        "after_first_reference",
        "after_next_page"
      ],
      "reference_in_text": {
        "word": "таблица",
        "number": true
      },
      "title_position": "above_left",
      "title_format": {
        "capitalize_first_letter": true,
        "end_with_period": false,
        "line_spacing": "1"
      },
      "large_tables": {
        "split": true,
        "continuation_word": "Продолжение таблицы",
        "column_headers_on_each_page": true
      },
      "numbering": {
        "style": "ARABIC",
        "continuous": true,
        "per_section": true,
        "appendices": {
          "separate_numbering": true,
          "prefix": "{appendix_id}."
        }
      },
      "headers_alignment": {
        "columns": "center",
        "rows": "left"
      },
      "font_size": "smaller_than_main_text"
    },
    "notes_and_footnotes": {
      "notes": {
        "object_position": "after_text",
        "word": "Примечание",
        "numbering_style": "ARABIC",
        "end_with_period": false
      },
      "footnotes": {
        "object_position": "page_end",
        "separator_line": [
          "short",
          "thin",
          "left_aligned"
        ],
        "style": [
          "ARABIC",
          "ASTERISK"
        ]
      }
    },
    "formulas": {
      "position": "center",
      "spacing": [
        "above",
        "below"
      ],
      "numbering": {
        "style": "ARABIC",
        "continuous": true,
        "position": "right",
        "brackets": "ROUND_BRACKETS"
      },
      "references_in_text": {
        "in_text_format": "({formula_number})"
      },
      "appendices": {
        "separate_numbering": true,
        "prefix": "appendix"
      }
    },
    "references": {
      "numbering_style": "ARABIC",
      "brackets": "SQUARE_BRACKETS",
      "continuous_numbering": true,
      "within_section_numbering": false
    },
    "cover_page": {
      "ministry_name": {
        "position": [
          "top",
          "center"
        ],
        "capitalization": "first_letter"
      },
      "organization_name": {
        "full_name": {
          "capitalization": "all",
          "position": "center",
          "line_spacing": "1"
        },
        "short_name": {
          "position": "center",
          "brackets": "ROUND_BRACKETS",
          "capitalization": "all",
          "line_spacing": "1"
        }
      },
      "index_and_registration": {
        "position": "left",
        "line_spacing": "1"
      },
      "UDK_index": {
        "position": "left",
        "spacing_above": "2"
      },
      "approval_signatures": {
        "words": [
          "СОГЛАСОВАНО",
          "УТВЕРЖДАЮ"
        ],
        "words_position": [
          "left",
          "right"
        ],
        "titles_and_names": {
          "title_first": true,
          "use_initials": true,
          "line_spacing": 1
        },
        "date_format": "dd.mm.yyyy"
      },
      "report_type": {
        "top_spacing": 2,
        "text": "ОТЧЕТ\nО НАУЧНО-ИССЛЕДОВАТЕЛЬСКОЙ РАБОТЕ",
        "position": "center",
        "line_spacing": 1
      },
      "NIR_name": {
        "top_spacing": 1,
        "position": "center",
        "capitalization": "first_letter",
        "line_spacing": 1
      },
      "report_name": {
        "position": "center",
        "capitalization": "all",
        "line_spacing": 1,
        "required": false
      },
      "report_kind": {
        "brackets": "ROUND_BRACKETS",
        "capitalization": "nothing"
      },
      "program_code": {
        "position": "center",
        "line_spacing": 1
      },
      "book_number": {
        "position": "center",
        "line_spacing": 1,
        "required": false
      },
      "author_signatures": {
        "titles_position": "left",
        "signature_position": "right"
      },
      "location_and_year": {
        "position": [
          "center",
          "bottom"
        ]
      }
    },
    "authors_list": {
      "format": "column",
      "titles_position": "left",
      "signature_position": "right",
      "section_involved": {
        "position": "right",
        "brackets": "ROUND_BRACKETS"
      }
    },
    "abstract": {
      "basic_info_format": {
        "commas_between": true,
        "indent": false
      },
      "keywords_format": {
        "capitalization": "all",
        "commas_between": true,
        "indent": false
      }
    },
    "table_of_contents": {
      "titles_alignment": "left",
      "page_number_alignment": "right",
      "symbol_between": "."
    },
    "terms_and_definitions": {
      "format": "column",
      "punctuation": false,
      "terms_alignment": "left",
      "terms_order": "alphabetical",
      "definitions_divisor": "-",
      "alternative_format": [
        "term",
        "definition"
      ]
    },
    "abbreviations_and_symbols": {
      "format": "column",
      "punctuation": false,
      "terms_alignment": "left",
      "terms_order": "alphabetical",
      "definitions_divisor": "-"
    },
    "bibliography": {
      "order": "appearance",
      "numbering_style": "{ARABIC}."
    },
    "appendices": {
      "allowed_content": [
        "graphics",
        "tables",
        "calculations",
        "algorithms",
        "program_descriptions"
      ],
      "placement_order": "appearance",
      "new_page_for_each": true,
      "title_format": {
        "word": "ПРИЛОЖЕНИЕ",
        "position": "center",
        "no_period": true
      },
      "numbering": {
        "allowed_letters": "АБВГДЕЖИКЛМНПРСТУФХЦШЭЮЯ",
        "one_appendix_numbering": true,
        "section_and_subsection_numbering": "ARABIC",
        "continuous": true
      }
    },
    "structural_elements": [
      "cover_page",
      "СПИСОК ИСПОЛНИТЕЛЕЙ",
      "РЕФЕРАТ",
      "СОДЕРЖАНИЕ",
      "ТЕРМИНЫ И ОПРЕДЕЛЕНИЯ",
      "ПЕРЕЧЕНЬ СОКРАЩЕНИЙ И ОБОЗНАЧЕНИЙ",
      "ВВЕДЕНИЕ",
      "main_body",
      "ЗАКЛЮЧЕНИЕ",
      "СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ",
      "ПРИЛОЖЕНИЕ"
    ]
  }
}
    ';
BEGIN
    IF NOT EXISTS (SELECT 1 FROM standarts WHERE standart_name = v_standart_name) THEN
        INSERT INTO standarts (standart_name, standart_json) VALUES (v_standart_name, v_file_content);
    END IF;
END
$$;