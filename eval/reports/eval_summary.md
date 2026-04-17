# Evaluation Summary

Total examples: 80

| Field | Accuracy |
| --- | ---: |
| garment_type | 40.00% |
| style | 60.00% |
| material | 0.00% |
| color_palette | 0.00% |
| pattern | 20.00% |
| season | 41.25% |
| occasion | 80.00% |
| consumer_profile | 60.00% |
| trend_notes | 0.00% |
| location_context | 80.00% |

## Confusion Analysis

### material
- expected `unknown`, predicted `cotton blend`: 45
- expected `unknown`, predicted `cotton`: 9
- expected `unknown`, predicted `leather or heavy cotton`: 10
- expected `cotton`, predicted `cotton blend`: 14
- expected `cotton`, predicted `leather or heavy cotton`: 2

### color_palette
- expected `black`, predicted `black|gray|red`: 7
- expected `black`, predicted `black|gray`: 5
- expected `black`, predicted `black|gray|white`: 3
- expected `black`, predicted `black|red`: 1
- expected `red`, predicted `black|gray|red`: 9
- expected `red`, predicted `black|blue|red`: 2
- expected `red`, predicted `black|gray|white`: 2
- expected `red`, predicted `gray|red`: 1
- expected `red`, predicted `gray|red|white`: 1
- expected `red`, predicted `black|red`: 1
- expected `unknown`, predicted `gray|red`: 6
- expected `unknown`, predicted `black|gray|red`: 7
- expected `unknown`, predicted `black|gray|white`: 4
- expected `unknown`, predicted `black|gray`: 12
- expected `unknown`, predicted `gray|white`: 1
- expected `unknown`, predicted `gray|green|white`: 1
- expected `unknown`, predicted `black|green`: 1
- expected `white`, predicted `black|gray|red`: 3
- expected `white`, predicted `black|gray|white`: 8
- expected `white`, predicted `black|blue|gray`: 1
- expected `white`, predicted `blue|gray|red`: 1
- expected `white`, predicted `gray|red|white`: 1
- expected `white`, predicted `black|gray`: 1
- expected `white`, predicted `gray|white`: 1

### pattern
- expected `unknown`, predicted `printed`: 36
- expected `unknown`, predicted `solid`: 12
- expected `solid`, predicted `printed`: 16

### trend_notes
- expected `pexels fashion image`, predicted `local visual fallback detected gray, black, red color cues and a printed surface. add openai_api_key for true multimodal garment reasoning.`: 6
- expected `pexels fashion image`, predicted `local visual fallback detected gray, black color cues and a printed surface. add openai_api_key for true multimodal garment reasoning.`: 7
- expected `pexels fashion image`, predicted `local visual fallback detected gray, black, red color cues and a solid surface. add openai_api_key for true multimodal garment reasoning.`: 3
- expected `pexels fashion image`, predicted `local visual fallback detected gray, black color cues and a solid surface. add openai_api_key for true multimodal garment reasoning.`: 1
- expected `pexels fashion image`, predicted `local visual fallback detected black, gray color cues and a printed surface. add openai_api_key for true multimodal garment reasoning.`: 4
- expected `pexels fashion image`, predicted `local visual fallback detected gray, white, black color cues and a printed surface. add openai_api_key for true multimodal garment reasoning.`: 4
- expected `pexels fashion image`, predicted `local visual fallback detected gray, red, black color cues and a printed surface. add openai_api_key for true multimodal garment reasoning.`: 3
- expected `pexels fashion image`, predicted `local visual fallback detected gray, black, white color cues and a printed surface. add openai_api_key for true multimodal garment reasoning.`: 6
- expected `pexels fashion image`, predicted `local visual fallback detected black, gray, red color cues and a printed surface. add openai_api_key for true multimodal garment reasoning.`: 3
- expected `pexels fashion image`, predicted `local visual fallback detected black, red, gray color cues and a solid surface. add openai_api_key for true multimodal garment reasoning.`: 2
- expected `pexels fashion image`, predicted `local visual fallback detected black, red color cues and a printed surface. add openai_api_key for true multimodal garment reasoning.`: 2
- expected `pexels fashion image`, predicted `local visual fallback detected red, gray, black color cues and a solid surface. add openai_api_key for true multimodal garment reasoning.`: 1
- expected `pexels fashion image`, predicted `local visual fallback detected black, red, blue color cues and a printed surface. add openai_api_key for true multimodal garment reasoning.`: 1
- expected `pexels fashion image`, predicted `local visual fallback detected black, gray, red color cues and a solid surface. add openai_api_key for true multimodal garment reasoning.`: 2
- expected `pexels fashion image`, predicted `local visual fallback detected white, gray, black color cues and a printed surface. add openai_api_key for true multimodal garment reasoning.`: 3
- expected `pexels fashion image`, predicted `local visual fallback detected gray, red, black color cues and a solid surface. add openai_api_key for true multimodal garment reasoning.`: 1
- expected `pexels fashion image`, predicted `local visual fallback detected red, black, gray color cues and a printed surface. add openai_api_key for true multimodal garment reasoning.`: 2
- expected `pexels fashion image`, predicted `local visual fallback detected red, gray color cues and a solid surface. add openai_api_key for true multimodal garment reasoning.`: 1
- expected `pexels fashion image`, predicted `local visual fallback detected gray, white, red color cues and a printed surface. add openai_api_key for true multimodal garment reasoning.`: 1
- expected `pexels fashion image`, predicted `local visual fallback detected blue, red, black color cues and a printed surface. add openai_api_key for true multimodal garment reasoning.`: 1
- expected `pexels fashion image`, predicted `local visual fallback detected black, gray, blue color cues and a printed surface. add openai_api_key for true multimodal garment reasoning.`: 1
- expected `pexels fashion image`, predicted `local visual fallback detected gray, red, blue color cues and a printed surface. add openai_api_key for true multimodal garment reasoning.`: 1
- expected `pexels fashion image`, predicted `local visual fallback detected gray, red, white color cues and a printed surface. add openai_api_key for true multimodal garment reasoning.`: 1
- expected `pexels fashion image`, predicted `local visual fallback detected gray, white color cues and a printed surface. add openai_api_key for true multimodal garment reasoning.`: 1
- expected `pexels fashion image`, predicted `local visual fallback detected white, green, gray color cues and a printed surface. add openai_api_key for true multimodal garment reasoning.`: 1
- expected `pexels fashion image`, predicted `local visual fallback detected gray, red color cues and a printed surface. add openai_api_key for true multimodal garment reasoning.`: 4
- expected `pexels fashion image`, predicted `local visual fallback detected green, black color cues and a printed surface. add openai_api_key for true multimodal garment reasoning.`: 1
- expected `pexels streetwear image`, predicted `local visual fallback detected red, gray color cues and a printed surface. add openai_api_key for true multimodal garment reasoning.`: 1
- expected `pexels streetwear image`, predicted `local visual fallback detected black, gray, red color cues and a printed surface. add openai_api_key for true multimodal garment reasoning.`: 1
- expected `pexels streetwear image`, predicted `local visual fallback detected gray, white, black color cues and a printed surface. add openai_api_key for true multimodal garment reasoning.`: 1
- expected `pexels streetwear image`, predicted `local visual fallback detected gray, black color cues and a printed surface. add openai_api_key for true multimodal garment reasoning.`: 4
- expected `pexels streetwear image`, predicted `local visual fallback detected black, gray color cues and a printed surface. add openai_api_key for true multimodal garment reasoning.`: 2
- expected `pexels streetwear image`, predicted `local visual fallback detected gray, black, white color cues and a printed surface. add openai_api_key for true multimodal garment reasoning.`: 2
- expected `pexels streetwear image`, predicted `local visual fallback detected gray, red color cues and a printed surface. add openai_api_key for true multimodal garment reasoning.`: 1
- expected `pexels streetwear image`, predicted `local visual fallback detected black, gray, white color cues and a printed surface. add openai_api_key for true multimodal garment reasoning.`: 1
- expected `pexels streetwear image`, predicted `local visual fallback detected gray, black, red color cues and a printed surface. add openai_api_key for true multimodal garment reasoning.`: 1
- expected `pexels streetwear image`, predicted `local visual fallback detected gray, black, red color cues and a solid surface. add openai_api_key for true multimodal garment reasoning.`: 1
- expected `pexels streetwear image`, predicted `local visual fallback detected gray, white color cues and a printed surface. add openai_api_key for true multimodal garment reasoning.`: 1

### style
- expected `festive`, predicted `casual`: 16
- expected `streetwear`, predicted `casual`: 16

### season
- expected `seasonless`, predicted `fall/winter`: 14
- expected `seasonless`, predicted `spring/summer`: 1
- expected `fall/winter`, predicted `seasonless`: 2
- expected `fall/winter`, predicted `spring/summer`: 1
- expected `spring/summer`, predicted `fall/winter`: 24
- expected `spring/summer`, predicted `seasonless`: 5

### occasion
- expected `celebration`, predicted `everyday`: 16

### consumer_profile
- expected `occasionwear customer`, predicted `general fashion customer`: 16
- expected `trend-led casual customer`, predicted `general fashion customer`: 16

### garment_type
- expected `jacket`, predicted `dress`: 16
- expected `top`, predicted `dress`: 16
- expected `skirt`, predicted `dress`: 16

### location_context
- expected `street`, predicted `unknown`: 16
