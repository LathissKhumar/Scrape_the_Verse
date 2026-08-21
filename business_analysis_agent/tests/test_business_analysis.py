import pytest
from unittest.mock import Mock, patch, MagicMock
from pydantic import ValidationError

from business_analysis.schemas.models import (
    BusinessInput,
    Evidence,
    BusinessProfile,
    BusinessType,
    BusinessModel,
    CompanyScale,
    MarketAnalysis,
    MarketCondition,
    DigitalAdoptionLevel,
    CustomerAnalysis,
    CustomerSegment,
    JourneyStage,
    CompetitorAnalysis,
    Competitor,
    ServiceAnalysis,
    Service,
    ServiceImportance,
    ServiceVisibility,
    BusinessProblem,
    ProblemSeverity,
    Opportunity,
    AgencyService,
    BusinessScore,
    ScoreCategory,
    FinalBusinessAnalysis,
    SourceType,
)
from business_analysis.state import BusinessAnalysisState, create_initial_state
from business_analysis.graph import build_business_analysis_graph


class TestInputValidation:
    def test_business_input_required_fields(self):
        input_data = BusinessInput(
            company_name="Test Corp",
            industry="Technology",
            location="San Francisco",
        )
        assert input_data.company_name == "Test Corp"
        assert input_data.industry == "Technology"
        assert input_data.location == "San Francisco"
        assert input_data.website is None

    def test_business_input_all_fields(self):
        input_data = BusinessInput(
            company_name="Test Corp",
            website="https://test.com",
            industry="Technology",
            location="San Francisco",
            description="A test company",
            products_services="Software",
            target_customers="Enterprises",
            additional_info="None",
        )
        assert input_data.website == "https://test.com"
        assert input_data.description == "A test company"

    def test_business_input_missing_required_raises(self):
        with pytest.raises(ValidationError):
            BusinessInput(industry="Tech", location="SF")

        with pytest.raises(ValidationError):
            BusinessInput(company_name="Test", location="SF")

        with pytest.raises(ValidationError):
            BusinessInput(company_name="Test", industry="Tech")


class TestStateCreation:
    def test_create_initial_state(self):
        input_data = BusinessInput(
            company_name="Test Corp",
            industry="Technology",
            location="San Francisco",
            website="https://test.com",
            description="Test desc",
        )

        state = create_initial_state(input_data)

        assert state["input_business"] == input_data
        assert len(state["evidence"]) >= 3
        assert state["business_profile"] is None
        assert state["market_analysis"] is None
        assert state["errors"] == []

    def test_create_initial_state_with_optional_fields(self):
        input_data = BusinessInput(
            company_name="Test Corp",
            industry="Technology",
            location="San Francisco",
            products_services="Software",
            target_customers="Enterprises",
        )

        state = create_initial_state(input_data)

        evidence_claims = [e.claim for e in state["evidence"]]
        assert any("Products/services" in c for c in evidence_claims)
        assert any("Target customers" in c for c in evidence_claims)


class TestPydanticModels:
    def test_evidence_model(self):
        evidence = Evidence(
            claim="Test claim",
            source="test",
            source_type=SourceType.MANUAL_INPUT,
            confidence=0.9,
        )
        assert evidence.claim == "Test claim"
        assert evidence.confidence == 0.9
        assert evidence.id is not None

    def test_business_profile_model(self):
        profile = BusinessProfile(
            business_type=BusinessType.LOCAL_SERVICE,
            business_model=BusinessModel.B2C,
            industry="Plumbing",
            geographic_market="Dallas, TX",
            primary_offerings=["Plumbing", "Drain cleaning"],
            company_scale=CompanyScale.SMALL,
        )
        assert profile.business_type == BusinessType.LOCAL_SERVICE
        assert len(profile.primary_offerings) == 2

    def test_market_analysis_model(self):
        analysis = MarketAnalysis(
            industry_overview="Growing market",
            market_condition=MarketCondition.GROWING,
            digital_adoption=DigitalAdoptionLevel.MODERATE,
            digital_opportunities=["SEO", "Local SEO"],
        )
        assert analysis.market_condition == MarketCondition.GROWING
        assert len(analysis.digital_opportunities) == 2

    def test_business_problem_model(self):
        problem = BusinessProblem(
            problem="Weak local visibility",
            evidence_ids=["e1", "e2"],
            business_impact=9,
            confidence=0.88,
            reasoning="Competitors rank higher",
            severity=ProblemSeverity.HIGH,
        )
        assert problem.business_impact == 9
        assert problem.severity == ProblemSeverity.HIGH

    def test_opportunity_model(self):
        opp = Opportunity(
            problem_reference="Weak local visibility",
            opportunity="Improve local SEO",
            recommended_services=[AgencyService.LOCAL_SEO, AgencyService.SEO],
            priority=9,
            rationale="High search volume",
            estimated_impact="High",
        )
        assert opp.priority == 9
        assert AgencyService.LOCAL_SEO in opp.recommended_services

    def test_business_score_model(self):
        score = BusinessScore(
            business_fit=80,
            digital_need=70,
            opportunity_value=75,
            evidence_confidence=85,
            serviceability=90,
            overall_score=77,
            priority=ScoreCategory.HIGH,
            score_explanation="Good fit",
        )
        assert score.overall_score == 77
        assert score.priority == ScoreCategory.HIGH

    def test_score_category_mapping(self):
        assert ScoreCategory.LOW.value == "LOW"
        assert ScoreCategory.MEDIUM.value == "MEDIUM"
        assert ScoreCategory.HIGH.value == "HIGH"
        assert ScoreCategory.VERY_HIGH.value == "VERY_HIGH"


class TestGraphConstruction:
    @patch("business_analysis.llm.get_llm")
    def test_graph_compiles(self, mock_get_llm):
        mock_llm = Mock()
        mock_get_llm.return_value = mock_llm

        graph = build_business_analysis_graph()
        assert graph is not None

    def test_graph_nodes_exist(self):
        graph = build_business_analysis_graph()
        nodes = graph.nodes.keys()

        expected_nodes = {
            "collect_initial_evidence",
            "business_profile",
            "parallel_analysis",
            "business_problem",
            "opportunity",
            "business_scoring",
            "generate_final_report",
        }

        for node in expected_nodes:
            assert node in nodes, f"Missing node: {node}"


class TestBusinessScoringCalculations:
    def test_calculate_business_fit(self):
        from business_analysis.agents.business_scoring import calculate_business_fit

        profile = BusinessProfile(
            business_type=BusinessType.LOCAL_SERVICE,
            business_model=BusinessModel.B2C,
            industry="Plumbing",
            geographic_market="Dallas",
            primary_offerings=["Plumbing"],
            company_scale=CompanyScale.SMALL,
        )
        market = MarketAnalysis(
            market_condition=MarketCondition.GROWING,
        )
        competitor = CompetitorAnalysis(
            competitors=[
                Competitor(name="Comp1"),
                Competitor(name="Comp2"),
                Competitor(name="Comp3"),
            ]
        )

        score = calculate_business_fit(profile, market, competitor)
        assert 0 <= score <= 100
        assert score > 50

    def test_calculate_digital_need(self):
        from business_analysis.agents.business_scoring import calculate_digital_need

        profile = BusinessProfile(
            business_type=BusinessType.LOCAL_SERVICE,
            business_model=BusinessModel.B2C,
            industry="Plumbing",
            geographic_market="Dallas",
            primary_offerings=["Plumbing"],
        )
        market = MarketAnalysis(
            digital_adoption=DigitalAdoptionLevel.HIGH,
        )
        service = ServiceAnalysis(
            overall_visibility=ServiceVisibility.NONE,
            key_gaps=["gap1", "gap2", "gap3", "gap4"],
        )
        competitor = CompetitorAnalysis(
            competitors=[
                Competitor(name="Comp1", digital_presence="strong"),
                Competitor(name="Comp2", digital_presence="strong"),
            ]
        )

        score = calculate_digital_need(profile, market, service, competitor)
        assert 0 <= score <= 100
        assert score > 60

    def test_calculate_overall_score(self):
        from business_analysis.agents.business_scoring import (
            calculate_business_fit,
            calculate_digital_need,
            calculate_opportunity_value,
            calculate_evidence_confidence,
            calculate_serviceability,
        )

        profile = BusinessProfile(
            business_type=BusinessType.LOCAL_SERVICE,
            business_model=BusinessModel.B2C,
            industry="Plumbing",
            geographic_market="Dallas",
            primary_offerings=["Plumbing"],
            company_scale=CompanyScale.SMALL,
        )
        market = MarketAnalysis(
            market_condition=MarketCondition.GROWING,
            digital_adoption=DigitalAdoptionLevel.HIGH,
        )
        service = ServiceAnalysis(
            overall_visibility=ServiceVisibility.LOW,
            key_gaps=["gap1", "gap2"],
        )
        competitor = CompetitorAnalysis(
            competitors=[
                Competitor(name="Comp1", digital_presence="strong"),
                Competitor(name="Comp2", digital_presence="strong"),
                Competitor(name="Comp3", digital_presence="moderate"),
            ]
        )
        problems = [
            BusinessProblem(
                problem="Test problem",
                evidence_ids=["e1"],
                business_impact=8,
                confidence=0.9,
                reasoning="Test",
                severity=ProblemSeverity.HIGH,
            )
        ]
        opportunities = [
            Opportunity(
                problem_reference="Test problem",
                opportunity="Test opportunity",
                recommended_services=[AgencyService.LOCAL_SEO, AgencyService.SEO],
                priority=8,
                rationale="Test",
                estimated_impact="High",
            )
        ]
        evidence = [
            Evidence(claim="Test", source="test", source_type=SourceType.MANUAL_INPUT, confidence=0.9),
        ]

        bf = calculate_business_fit(profile, market, competitor)
        dn = calculate_digital_need(profile, market, service, competitor)
        ov = calculate_opportunity_value(opportunities, problems)
        ec = calculate_evidence_confidence(evidence, problems)
        sv = calculate_serviceability(profile, opportunities)

        overall = int(0.20 * bf + 0.25 * dn + 0.25 * ov + 0.15 * ec + 0.15 * sv)

        assert 0 <= overall <= 100


class TestProblemToServiceMapping:
    def test_mapping_no_website(self):
        from business_analysis.agents.opportunity import map_problem_to_services

        problem = BusinessProblem(
            problem="Business has no website",
            evidence_ids=["e1"],
            business_impact=9,
            confidence=0.9,
            reasoning="No website found",
            severity=ProblemSeverity.CRITICAL,
        )

        services = map_problem_to_services(problem)
        assert AgencyService.NEW_WEBSITE in services

    def test_mapping_weak_local(self):
        from business_analysis.agents.opportunity import map_problem_to_services

        problem = BusinessProblem(
            problem="Weak local visibility in search",
            evidence_ids=["e1"],
            business_impact=8,
            confidence=0.85,
            reasoning="Not ranking locally",
            severity=ProblemSeverity.HIGH,
        )

        services = map_problem_to_services(problem)
        assert AgencyService.LOCAL_SEO in services

    def test_mapping_technical_seo(self):
        from business_analysis.agents.opportunity import map_problem_to_services

        problem = BusinessProblem(
            problem="Technical SEO problems on site",
            evidence_ids=["e1"],
            business_impact=7,
            confidence=0.8,
            reasoning="Crawl errors",
            severity=ProblemSeverity.HIGH,
        )

        services = map_problem_to_services(problem)
        assert AgencyService.TECHNICAL_SEO in services

    def test_mapping_content_gap(self):
        from business_analysis.agents.opportunity import map_problem_to_services

        problem = BusinessProblem(
            problem="Content gap for key services",
            evidence_ids=["e1"],
            business_impact=6,
            confidence=0.75,
            reasoning="Missing service pages",
            severity=ProblemSeverity.MEDIUM,
        )

        services = map_problem_to_services(problem)
        assert AgencyService.SEO in services
        assert AgencyService.CONTENT in services


class TestEvidenceHandling:
    def test_evidence_confidence_values(self):
        evidence = Evidence(
            claim="Test",
            source="test",
            source_type=SourceType.MANUAL_INPUT,
            confidence=1.0,
        )
        assert evidence.confidence == 1.0

        evidence2 = Evidence(
            claim="Test",
            source="test",
            source_type=SourceType.MANUAL_INPUT,
            confidence=0.0,
        )
        assert evidence2.confidence == 0.0

    def test_unknown_handling_in_models(self):
        profile = BusinessProfile(
            business_type=BusinessType.OTHER,
            business_model=BusinessModel.B2C,
            industry="Unknown",
            geographic_market="Unknown",
        )
        assert profile.business_type == BusinessType.OTHER
        assert profile.company_scale == CompanyScale.UNKNOWN

        market = MarketAnalysis(
            market_condition=MarketCondition.UNKNOWN,
            digital_adoption=DigitalAdoptionLevel.UNKNOWN,
        )
        assert market.market_condition == MarketCondition.UNKNOWN
        assert market.digital_adoption == DigitalAdoptionLevel.UNKNOWN


class TestMockedGraphInvocation:
    @patch("business_analysis.agents.business_profile.get_structured_llm")
    @patch("business_analysis.agents.market_analysis.get_structured_llm")
    @patch("business_analysis.agents.customer_analysis.get_structured_llm")
    @patch("business_analysis.agents.competitor_analysis.get_structured_llm")
    @patch("business_analysis.agents.service_analysis.get_structured_llm")
    @patch("business_analysis.agents.business_problem.get_structured_llm")
    @patch("business_analysis.agents.opportunity.get_structured_llm")
    @patch("business_analysis.agents.business_scoring.get_structured_llm")
    def test_graph_invocation_with_mocks(
        self,
        mock_scoring_llm,
        mock_opportunity_llm,
        mock_problem_llm,
        mock_service_llm,
        mock_competitor_llm,
        mock_customer_llm,
        mock_market_llm,
        mock_profile_llm,
    ):
        mock_profile_llm.return_value.invoke.return_value = BusinessProfile(
            business_type=BusinessType.LOCAL_SERVICE,
            business_model=BusinessModel.B2C,
            industry="Plumbing",
            geographic_market="Dallas",
            primary_offerings=["Plumbing"],
            company_scale=CompanyScale.SMALL,
        )

        mock_market_llm.return_value.invoke.return_value = MarketAnalysis(
            market_condition=MarketCondition.GROWING,
            digital_adoption=DigitalAdoptionLevel.MODERATE,
        )

        mock_customer_llm.return_value.invoke.return_value = CustomerAnalysis(
            segments=[],
            primary_customers=["Homeowners"],
        )

        mock_competitor_llm.return_value.invoke.return_value = CompetitorAnalysis(
            competitors=[Competitor(name="Competitor 1")],
            identified_gaps=["Local SEO"],
        )

        mock_service_llm.return_value.invoke.return_value = ServiceAnalysis(
            services=[],
            overall_visibility=ServiceVisibility.MODERATE,
        )

        mock_problem_llm.return_value.invoke.return_value = [
            BusinessProblem(
                problem="Weak local SEO",
                evidence_ids=["e1"],
                business_impact=8,
                confidence=0.85,
                reasoning="Not ranking",
                severity=ProblemSeverity.HIGH,
            )
        ]

        mock_opportunity_llm.return_value.invoke.return_value = [
            Opportunity(
                problem_reference="Weak local SEO",
                opportunity="Improve local rankings",
                recommended_services=[AgencyService.LOCAL_SEO],
                priority=9,
                rationale="High search volume",
                estimated_impact="High",
            )
        ]

        mock_scoring_llm.return_value.invoke.return_value = BusinessScore(
            business_fit=75,
            digital_need=70,
            opportunity_value=80,
            evidence_confidence=85,
            serviceability=80,
            overall_score=77,
            priority=ScoreCategory.HIGH,
            score_explanation="Test explanation",
        )

        graph = build_business_analysis_graph()

        input_data = BusinessInput(
            company_name="Test Plumbing",
            industry="Plumbing",
            location="Dallas, TX",
        )
        initial_state = create_initial_state(input_data)

        result = graph.invoke(initial_state)

        assert "final_report" in result
        assert result["final_report"] is not None
        assert result["final_report"].company_name == "Test Plumbing"
        # Score is calculated deterministically, verify it's in valid range
        assert 0 <= result["final_report"].business_score.overall_score <= 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])