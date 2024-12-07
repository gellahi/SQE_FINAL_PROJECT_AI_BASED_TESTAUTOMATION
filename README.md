# SQE_FINAL_PROJECT_AI_BASED_TESTAUTOMATION

# Run all components in sequence
python specs/api_parser.py
python test_cases/generate_tests.py
pytest tests/ -v --html=test_results/report.html
python ml/anomaly_detector.py
python ci_cd/report_generator.py