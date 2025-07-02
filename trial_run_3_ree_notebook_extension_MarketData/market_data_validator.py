"""
Market Data Validator - REE Market Intelligence Extension
Quality assurance for USGS market data integration
Built for EPO TIP Platform / PATLIB 2025 demonstration
"""

import pandas as pd
from typing import Dict, List, Tuple, Optional
import numpy as np
from datetime import datetime
import logging

class MarketDataValidator:
    """
    Quality assurance and validation for market intelligence data
    Ensures data integrity for business critical analysis
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validation_results = {}
        self.quality_thresholds = {
            'price_data_completeness': 80,
            'production_data_coverage': 75,
            'import_dependency_coverage': 70,
            'market_events_coverage': 60,
            'data_freshness_days': 365
        }
    
    def validate_market_data_structure(self, market_data: Dict) -> Dict[str, bool]:
        """Validate the structure and presence of required market data fields"""
        required_sections = [
            'price_trends',
            'import_dependency', 
            'global_production',
            'supply_concentration',
            'market_events'
        ]
        
        structure_validation = {}
        for section in required_sections:
            structure_validation[section] = section in market_data
            
        return structure_validation
    
    def validate_price_data_quality(self, price_df: pd.DataFrame) -> Dict[str, any]:
        """Validate price trend data quality and completeness"""
        validation = {
            'data_points': len(price_df),
            'year_range': None,
            'missing_values': price_df.isnull().sum().sum(),
            'negative_prices': (price_df['price_index'] < 0).sum() if 'price_index' in price_df.columns else 0,
            'price_volatility': None,
            'quality_score': 0
        }
        
        if not price_df.empty:
            validation['year_range'] = (price_df['year'].min(), price_df['year'].max())
            
            if 'price_index' in price_df.columns:
                validation['price_volatility'] = price_df['price_index'].std()
                
                # Calculate quality score
                completeness_score = min(100, (len(price_df) / 15) * 100)  # 15 years expected
                accuracy_score = max(0, 100 - (validation['negative_prices'] * 10))
                validation['quality_score'] = (completeness_score + accuracy_score) / 2
        
        return validation
    
    def validate_production_data_coverage(self, production_df: pd.DataFrame) -> Dict[str, any]:
        """Validate global production data coverage and quality"""
        validation = {
            'total_records': len(production_df),
            'countries_covered': production_df['country'].nunique() if 'country' in production_df.columns else 0,
            'years_covered': production_df['year'].nunique() if 'year' in production_df.columns else 0,
            'missing_values': production_df.isnull().sum().sum(),
            'negative_production': 0,
            'quality_score': 0
        }
        
        if not production_df.empty and 'production_tons' in production_df.columns:
            validation['negative_production'] = (production_df['production_tons'] < 0).sum()
            
            # Calculate quality score
            coverage_score = min(100, (validation['countries_covered'] / 10) * 100)  # 10 countries expected
            temporal_score = min(100, (validation['years_covered'] / 5) * 100)  # 5 years expected
            accuracy_score = max(0, 100 - (validation['negative_production'] * 5))
            validation['quality_score'] = (coverage_score + temporal_score + accuracy_score) / 3
        
        return validation
    
    def validate_import_dependency_data(self, import_data: Dict[str, float]) -> Dict[str, any]:
        """Validate import dependency data quality"""
        validation = {
            'elements_covered': len(import_data),
            'invalid_percentages': 0,
            'missing_critical_elements': [],
            'quality_score': 0
        }
        
        critical_elements = ['rare_earths', 'neodymium', 'dysprosium']
        
        for element in critical_elements:
            if element not in import_data:
                validation['missing_critical_elements'].append(element)
        
        # Check for invalid percentages
        for element, percentage in import_data.items():
            if not isinstance(percentage, (int, float)) or percentage < 0 or percentage > 100:
                validation['invalid_percentages'] += 1
        
        # Calculate quality score
        coverage_score = min(100, (validation['elements_covered'] / 6) * 100)  # 6 elements expected
        accuracy_score = max(0, 100 - (validation['invalid_percentages'] * 15))
        completeness_score = max(0, 100 - (len(validation['missing_critical_elements']) * 20))
        validation['quality_score'] = (coverage_score + accuracy_score + completeness_score) / 3
        
        return validation
    
    def validate_market_events_timeline(self, events: List[Dict]) -> Dict[str, any]:
        """Validate market events data for correlation analysis"""
        validation = {
            'total_events': len(events),
            'year_coverage': None,
            'missing_descriptions': 0,
            'chronological_order': True,
            'quality_score': 0
        }
        
        if events:
            years = [event.get('year') for event in events if 'year' in event]
            if years:
                validation['year_coverage'] = (min(years), max(years))
                validation['chronological_order'] = years == sorted(years)
            
            for event in events:
                if not event.get('description') or not event.get('event'):
                    validation['missing_descriptions'] += 1
            
            # Calculate quality score
            coverage_score = min(100, (validation['total_events'] / 8) * 100)  # 8 events expected
            completeness_score = max(0, 100 - (validation['missing_descriptions'] * 10))
            chronology_score = 100 if validation['chronological_order'] else 50
            validation['quality_score'] = (coverage_score + completeness_score + chronology_score) / 3
        
        return validation
    
    def calculate_overall_market_data_quality(self, 
                                            structure_validation: Dict,
                                            price_validation: Dict, 
                                            production_validation: Dict,
                                            import_validation: Dict,
                                            events_validation: Dict) -> Dict[str, any]:
        """Calculate comprehensive market data quality assessment"""
        
        # Structure completeness score
        structure_score = (sum(structure_validation.values()) / len(structure_validation)) * 100
        
        # Component quality scores
        component_scores = {
            'structure': structure_score,
            'price_data': price_validation.get('quality_score', 0),
            'production_data': production_validation.get('quality_score', 0),
            'import_dependency': import_validation.get('quality_score', 0),
            'market_events': events_validation.get('quality_score', 0)
        }
        
        # Weighted overall score
        weights = {
            'structure': 0.15,
            'price_data': 0.30,
            'production_data': 0.25,
            'import_dependency': 0.15,
            'market_events': 0.15
        }
        
        overall_score = sum(score * weights[component] for component, score in component_scores.items())
        
        # Quality rating
        if overall_score >= 90:
            quality_rating = "EXCELLENT"
        elif overall_score >= 80:
            quality_rating = "GOOD"
        elif overall_score >= 70:
            quality_rating = "ACCEPTABLE"
        elif overall_score >= 60:
            quality_rating = "NEEDS_IMPROVEMENT"
        else:
            quality_rating = "POOR"
        
        return {
            'overall_score': round(overall_score, 2),
            'quality_rating': quality_rating,
            'component_scores': component_scores,
            'business_confidence': "HIGH" if overall_score >= 80 else "MEDIUM" if overall_score >= 60 else "LOW",
            'validation_timestamp': datetime.now().isoformat()
        }
    
    def generate_market_data_quality_report(self, market_data_collector) -> Dict:
        """Generate comprehensive quality assessment report"""
        
        # Load and validate market data
        market_data = market_data_collector.load_market_data()
        
        # Run all validations
        structure_validation = self.validate_market_data_structure(market_data)
        
        price_df = market_data_collector.get_price_trends('neodymium')
        price_validation = self.validate_price_data_quality(price_df)
        
        production_df = market_data_collector.get_global_production_data()
        production_validation = self.validate_production_data_coverage(production_df)
        
        import_data = market_data_collector.get_import_dependency_data()
        import_validation = self.validate_import_dependency_data(import_data)
        
        events = market_data_collector.get_market_events_timeline()
        events_validation = self.validate_market_events_timeline(events)
        
        # Calculate overall quality
        overall_assessment = self.calculate_overall_market_data_quality(
            structure_validation, price_validation, production_validation,
            import_validation, events_validation
        )
        
        # Compile comprehensive report
        quality_report = {
            'market_data_quality_assessment': overall_assessment,
            'detailed_validations': {
                'structure': structure_validation,
                'price_data': price_validation,
                'production_data': production_validation,
                'import_dependency': import_validation,
                'market_events': events_validation
            },
            'recommendations': self.generate_improvement_recommendations(overall_assessment)
        }
        
        return quality_report
    
    def generate_improvement_recommendations(self, assessment: Dict) -> List[str]:
        """Generate actionable recommendations for data quality improvement"""
        recommendations = []
        
        overall_score = assessment['overall_score']
        component_scores = assessment['component_scores']
        
        if component_scores['price_data'] < 80:
            recommendations.append("Enhance price data coverage - consider additional REE elements")
        
        if component_scores['production_data'] < 80:
            recommendations.append("Expand production data to include more countries and recent years")
        
        if component_scores['import_dependency'] < 80:
            recommendations.append("Update import dependency data with latest trade statistics")
        
        if component_scores['market_events'] < 80:
            recommendations.append("Add more detailed market event descriptions and impact analysis")
        
        if overall_score < 90:
            recommendations.append("Consider integrating additional data sources for enhanced reliability")
        
        return recommendations

# Testing function
def test_market_data_validator():
    """Test market data validator functionality"""
    from usgs_market_collector import USGSMarketDataCollector
    
    validator = MarketDataValidator()
    collector = USGSMarketDataCollector()
    
    # Generate comprehensive quality report
    quality_report = validator.generate_market_data_quality_report(collector)
    
    assert quality_report is not None, "Failed to generate quality report"
    print("✅ Quality report generated successfully")
    
    assessment = quality_report['market_data_quality_assessment']
    print(f"✅ Overall quality score: {assessment['overall_score']}")
    print(f"✅ Quality rating: {assessment['quality_rating']}")
    print(f"✅ Business confidence: {assessment['business_confidence']}")
    
    detailed = quality_report['detailed_validations']
    print(f"✅ Structure validation: {sum(detailed['structure'].values())}/{len(detailed['structure'])} sections")
    print(f"✅ Price data quality: {detailed['price_data']['quality_score']:.1f}")
    print(f"✅ Production data quality: {detailed['production_data']['quality_score']:.1f}")
    
    recommendations = quality_report['recommendations']
    print(f"✅ Generated {len(recommendations)} improvement recommendations")
    
    print("\n🎯 All market data validation tests passed!")
    return True

if __name__ == "__main__":
    test_market_data_validator()