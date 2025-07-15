"""
Item pipeline that uses OpenAI function calling to extract structured company info.
Enhancements:
- Clear system and user prompts with explicit instructions
- Few-shot examples for edge cases
- Confidence status flag for deduced vs explicit data
"""
import os
import json
import datetime
import openai
# from .config import settings
from companyinfo.config import settings

class CompanyInfoPipeline:
    def open_spider(self, spider):
        # Initialize OpenAI API key and model
        openai.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        # Define the function schema for extraction
        self.function = {
            'name': 'extract_company_info',
            'description': 'Extracts manufacturing, outsourcing, and corporate affiliation details from text.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'domain': {'type':'string', 'description':'Company website domain.'},
                    'company_name': {'type':'string', 'description':'Official company name.'},
                    'manufactures_in_house': {
                        'type':'string',
                        'enum':['Yes','No','Partial'],
                        'description':'Whether the company manufactures in-house.'
                    },
                    'in_house_details': {'type':'string', 'description':'Details of in-house production if applicable.'},
                    'outsourced': {
                        'type':'string',
                        'enum':['Yes','No','Partial'],
                        'description':'Whether any production is outsourced.'
                    },
                    'outsourcing_partners': {
                        'type':'array',
                        'description':'List of third-party manufacturers if outsourced.',
                        'items': {
                            'type':'object',
                            'properties': {
                                'name': {'type':'string', 'description':'Partner company name.'},
                                'website': {'type':'string', 'description':'Partner website URL.'},
                                'contact': {'type':'string', 'description':'Contact email or phone if available.'}
                            },
                            'required':['name','website'],
                            'additionalProperties': False
                        }
                    },
                    'parent_company': {'type':'string', 'description':'Name of parent company if any.'},
                    'affiliate_companies': {
                        'type':'array',
                        'description':'List of affiliate or sister companies.',
                        'items': {'type':'string'}
                    },
                    'extraction_status': {
                        'type':'string',
                        'enum':['explicit','deduced','not_found'],
                        'description':'Indicates if data was explicitly mentioned, deduced, or not found.'
                    }
                },
                'required':[ 'domain','company_name','manufactures_in_house','outsourced','outsourcing_partners','parent_company','affiliate_companies','extraction_status']
            }
        }

    def process_item(self, item, spider):
        # Truncate raw_text to fit within token limits
        raw = item.get('raw_text','')
        text = raw if len(raw) < 12000 else raw[-12000:]

        # System prompt with instructions
        system_msg = {
            'role':'system',
            'content':(
                "You are an assistant specialized in extracting structured company information. "
                "Only use the provided text and do not add external information. "
                "If a fact is not explicitly mentioned but can be reasonably deduced, set extraction_status to 'deduced'. "
                "If no information is found for a field, set it to null or 'not_found'."
            )
        }

                # User prompt with context and few-shot examples
        user_msg = {
            'role':'user',
            'content': f"""
                Extract the following JSON for the company:
                Domain: {item['domain']}
                Company Name: {item['company_name']}
                Text:
                {text}

                Example output for a known company:
                {{
                "domain": "sample.com",
                "company_name": "Sample Inc.",
                "manufactures_in_house": "No",
                "in_house_details": null,
                "outsourced": "Yes",
                "outsourcing_partners": [
                    {{"name": "ACME Co.", "website": "acme.com", "contact": null}}
                ],
                "parent_company": "Global Holdings",
                "affiliate_companies": [],
                "extraction_status": "explicit"
                }}
            """
        }

        # Call OpenAI ChatCompletion with function calling
        response = openai.chat.completions.create(
            model=self.model,
            messages=[system_msg, user_msg],
            functions=[self.function],
            function_call={'name': self.function['name']}
        )

        
        msg = response.choices[0].message
        args = {}
        # if msg.get('function_call'):
        #     try:
        #         args = json.loads(msg.function_call.arguments)
        #     except json.JSONDecodeError:
        #         spider.logger.error('Failed to decode function_call arguments')
        fc = getattr(msg, 'function_call', None)
        if fc and fc.arguments:
            try:
                args = json.loads(fc.arguments)
            except json.JSONDecodeError:
                spider.logger.error('Failed to parse JSON from function_call.arguments')

        # Merge extracted data into item
        for field in self.function['parameters']['properties']:
            item[field] = args.get(field)

        # Ensure last_updated is added
        item['last_updated'] = datetime.date.today().isoformat()
        return item