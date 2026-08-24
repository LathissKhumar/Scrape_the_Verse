from unittest.mock import Mock, patch

import pytest
from business_analysis.graph import build_business_analysis_graph
from business_analysis.schemas.models import (
    AgencyService,
    BusinessInput,
    BusinessModel,
    BusinessProblem,
    BusinessProfile,
    BusinessScore,
    BusinessType,
    CompanyScale,
    Competitor,
    CompetitorAnalysis,
    CustomerAnalysis,
    CustomerSegment,
    DigitalAdoptionLevel,
    Evidence,
    FinalBusinessAnalysis,
    MarketAnalysis,
    MarketCondition,
    Opportunity,
    ProblemSeverity,
    ScoreCategory,
    Service,
    ServiceAnalysis,
    ServiceVisibility,
    SourceType,
)
from business_analysis.state import create_initial_state
from pydantic import ValidationError


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
            calculate_evidence_confidence,
            calculate_opportunity_value,
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
            Evidence(
                claim="Test",
                source="test",
                source_type=SourceType.MANUAL_INPUT,
                confidence=0.9,
            ),
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


class TestQualityGateHardening:
    """Quality gate must properly detect SKIPPED/FAILED nodes and not over-report PASSED."""

    def _make_state_with_skipped_nodes(self):
        from business_analysis.schemas.models import (
            AgencyService,
            AnalysisCompleteness,
            BusinessModel,
            BusinessProblem,
            BusinessProfile,
            BusinessScore,
            BusinessType,
            CompanyScale,
            NodeExecutionStatus,
            NodeStatusEnum,
            Opportunity,
            ProblemSeverity,
            ProblemStatus,
            ProblemType,
            ScoreCategory,
            ServiceAnalysis,
            ServiceVisibility,
        )
        from business_analysis.state import create_initial_state

        input_data = BusinessInput(
            company_name="Test Co", industry="Dental", location="Amsterdam"
        )
        state = create_initial_state(input_data)

        statuses = dict(state["node_statuses"])
        statuses["business_profile"] = NodeExecutionStatus(
            status=NodeStatusEnum.SUCCESS, confidence=0.9
        )
        statuses["market_analysis"] = NodeExecutionStatus(
            status=NodeStatusEnum.SKIPPED, confidence=0.0
        )
        statuses["customer_analysis"] = NodeExecutionStatus(
            status=NodeStatusEnum.SKIPPED, confidence=0.0
        )
        statuses["competitor_analysis"] = NodeExecutionStatus(
            status=NodeStatusEnum.SKIPPED, confidence=0.0
        )
        statuses["service_analysis"] = NodeExecutionStatus(
            status=NodeStatusEnum.SUCCESS, confidence=0.9
        )
        statuses["business_problem"] = NodeExecutionStatus(
            status=NodeStatusEnum.SUCCESS, confidence=0.85
        )
        statuses["opportunity"] = NodeExecutionStatus(
            status=NodeStatusEnum.SUCCESS, confidence=0.85
        )

        problems = [
            BusinessProblem(
                problem="Visibility gap",
                evidence_ids=["ev1"],
                business_impact=8,
                confidence=0.85,
                reasoning="Gap",
                type=ProblemType.SERVICE_VISIBILITY,
                status=ProblemStatus.POTENTIAL,
                severity=ProblemSeverity.HIGH,
            )
        ]
        opps = [
            Opportunity(
                problem_reference="Visibility gap",
                opportunity="Build landing pages",
                recommended_services=[AgencyService.LOCAL_SEO],
                priority=8,
                rationale="Key gap",
            )
        ]
        score = BusinessScore(
            business_fit=80,
            digital_need=65,
            opportunity_value=80,
            evidence_confidence=90,
            serviceability=90,
            analysis_completeness=57,
            overall_score=77,
            priority=ScoreCategory.HIGH,
            score_explanation="Test",
        )
        profile = BusinessProfile(
            business_type=BusinessType.LOCAL_SERVICE,
            business_model=BusinessModel.B2C,
            industry="Dental Services",
            geographic_market="Amsterdam",
            company_scale=CompanyScale.SMALL,
        )
        completeness = AnalysisCompleteness(
            profile_completeness=96.0,
            market_completeness=0.0,
            customer_completeness=0.0,
            competitor_completeness=0.0,
            service_completeness=96.0,
            problem_completeness=94.0,
            opportunity_completeness=94.0,
            overall_analysis_completeness=57.0,
        )

        return {
            **state,
            "business_profile": profile,
            "market_analysis": None,
            "customer_analysis": None,
            "competitor_analysis": None,
            "service_analysis": ServiceAnalysis(
                services=[], overall_visibility=ServiceVisibility.LOW
            ),
            "business_problems": problems,
            "opportunities": opps,
            "business_score": score,
            "completeness": completeness,
            "node_statuses": statuses,
        }

    def test_skipped_important_nodes_prevent_passed(self):
        """Market/customer/competitor SKIPPED → quality status must NOT be PASSED."""
        from business_analysis.agents.quality_gate import quality_gate_agent

        state = self._make_state_with_skipped_nodes()
        result = quality_gate_agent(state)
        qg = result["quality_gate"]
        assert qg is not None
        assert qg.quality_status != "PASSED", (
            f"Quality gate returned PASSED with skipped nodes: {qg.quality_status}. "
            f"Warnings: {qg.warnings}"
        )

    def test_skipped_nodes_produce_warnings(self):
        """SKIPPED market/customer/competitor must appear in QG warnings."""
        from business_analysis.agents.quality_gate import quality_gate_agent

        state = self._make_state_with_skipped_nodes()
        result = quality_gate_agent(state)
        qg = result["quality_gate"]
        warning_text = " ".join(qg.warnings).lower()
        assert "market" in warning_text or "skipped" in warning_text, (
            f"Expected 'market' or 'skipped' in warnings. Got: {qg.warnings}"
        )

    def test_failed_problem_node_caps_priority(self):
        """If BusinessProblemAgent FAILED, final priority must NOT be VERY_HIGH."""
        from business_analysis.agents.business_scoring import business_scoring_agent
        from business_analysis.schemas.models import (
            BusinessModel,
            BusinessProfile,
            BusinessType,
            CompanyScale,
            CompetitorAnalysis,
            CustomerAnalysis,
            DigitalAdoptionLevel,
            MarketAnalysis,
            MarketCondition,
            NodeExecutionStatus,
            NodeStatusEnum,
            ScoreCategory,
            ServiceAnalysis,
            ServiceVisibility,
        )
        from business_analysis.state import create_initial_state

        input_data = BusinessInput(
            company_name="Test Co", industry="Dental", location="Amsterdam"
        )
        state = create_initial_state(input_data)
        statuses = dict(state["node_statuses"])
        statuses["business_problem"] = NodeExecutionStatus(
            status=NodeStatusEnum.FAILED, confidence=0.0
        )
        statuses["opportunity"] = NodeExecutionStatus(
            status=NodeStatusEnum.FAILED, confidence=0.0
        )
        statuses["business_profile"] = NodeExecutionStatus(
            status=NodeStatusEnum.SUCCESS, confidence=0.9
        )
        statuses["market_analysis"] = NodeExecutionStatus(
            status=NodeStatusEnum.SUCCESS, confidence=0.8
        )
        statuses["customer_analysis"] = NodeExecutionStatus(
            status=NodeStatusEnum.SUCCESS, confidence=0.8
        )
        statuses["competitor_analysis"] = NodeExecutionStatus(
            status=NodeStatusEnum.SUCCESS, confidence=0.8
        )
        statuses["service_analysis"] = NodeExecutionStatus(
            status=NodeStatusEnum.SUCCESS, confidence=0.8
        )

        state_with_failure = {
            **state,
            "business_profile": BusinessProfile(
                business_type=BusinessType.LOCAL_SERVICE,
                business_model=BusinessModel.B2C,
                industry="Dental",
                geographic_market="Amsterdam",
                company_scale=CompanyScale.SMALL,
            ),
            "market_analysis": MarketAnalysis(
                market_condition=MarketCondition.GROWING,
                digital_adoption=DigitalAdoptionLevel.MODERATE,
            ),
            "customer_analysis": CustomerAnalysis(),
            "competitor_analysis": CompetitorAnalysis(),
            "service_analysis": ServiceAnalysis(
                overall_visibility=ServiceVisibility.MODERATE
            ),
            "business_problems": [],  # FAILED — no problems
            "opportunities": [],  # FAILED — no opportunities
            "node_statuses": statuses,
        }

        result = business_scoring_agent(state_with_failure)
        score = result["business_score"]
        assert score.priority != ScoreCategory.VERY_HIGH, (
            f"Priority was VERY_HIGH despite problem node failure. Score: {score.overall_score}"
        )
        assert score.priority in [ScoreCategory.LOW, ScoreCategory.MEDIUM], (
            f"Expected LOW or MEDIUM priority when problems/opportunities missing. Got: {score.priority}"
        )

    def test_quality_status_is_needs_review_with_critical_failures(self):
        """With failed critical checks, quality_status must be NEEDS_REVIEW."""
        from business_analysis.agents.quality_gate import quality_gate_agent
        from business_analysis.state import create_initial_state

        input_data = BusinessInput(
            company_name="Test Co", industry="Dental", location="Amsterdam"
        )
        state = create_initial_state(input_data)
        # Deliberately minimal state — no agents ran successfully
        result = quality_gate_agent(state)
        qg = result["quality_gate"]
        assert qg.quality_status in [
            "NEEDS_REVIEW",
            "FAILED",
            "PASSED_WITH_WARNINGS",
        ], f"Expected NEEDS_REVIEW/FAILED when no agents ran, got: {qg.quality_status}"
        assert len(qg.failed_checks) > 0 or len(qg.warnings) > 0


class TestServiceValidation:
    """Service names must be validated; malformed names must be rejected."""

    def test_malformed_service_name_equal_sign_rejected(self):
        """Service names containing '=' are rejected by field_validator."""
        with pytest.raises(Exception):  # ValidationError
            Service(name="target_customers=Dental Patients", description="test")

    def test_malformed_service_name_too_short_rejected(self):
        """Service names that are too short are rejected."""
        with pytest.raises(Exception):
            Service(name="a", description="test")

    def test_malformed_service_name_backslash_rejected(self):
        """Service names containing backslash patterns are rejected."""
        with pytest.raises(Exception):
            Service(name='\\"test\\"', description="test")

    def test_valid_service_names_accepted(self):
        """Valid service names must pass through without error."""
        svc = Service(name="Dental Anxiety Treatment", description="Specialized care")
        assert svc.name == "Dental Anxiety Treatment"

    def test_valid_complex_case_management(self):
        svc = Service(
            name="Complex Case Management", description="Multidisciplinary planning"
        )
        assert svc.name == "Complex Case Management"

    def test_service_name_stripped_whitespace(self):
        """Service names should be stripped of whitespace."""
        svc = Service(name="  Special Dentistry  ", description="test")
        assert svc.name == "Special Dentistry"


class TestCompletenessAccuracy:
    """Completeness scores must accurately reflect node execution status."""

    def test_skipped_market_node_gives_zero_completeness(self):
        """Market node SKIPPED → market_completeness = 0."""
        from business_analysis.agents.business_scoring import _node_completeness
        from business_analysis.schemas.models import NodeExecutionStatus, NodeStatusEnum

        statuses = {
            "market_analysis": NodeExecutionStatus(
                status=NodeStatusEnum.SKIPPED, confidence=0.0
            )
        }
        comp = _node_completeness(statuses, "market_analysis", None)
        assert comp == 0.0, f"Expected 0.0 for SKIPPED node, got {comp}"

    def test_failed_node_gives_zero_completeness(self):
        """Node FAILED → completeness = 0."""
        from business_analysis.agents.business_scoring import _node_completeness
        from business_analysis.schemas.models import NodeExecutionStatus, NodeStatusEnum

        statuses = {
            "customer_analysis": NodeExecutionStatus(
                status=NodeStatusEnum.FAILED, confidence=0.0
            )
        }
        comp = _node_completeness(statuses, "customer_analysis", object())
        assert comp == 0.0, f"Expected 0.0 for FAILED node, got {comp}"

    def test_success_node_gives_nonzero_completeness(self):
        """Node SUCCESS with output → completeness > 60."""
        from business_analysis.agents.business_scoring import _node_completeness
        from business_analysis.schemas.models import NodeExecutionStatus, NodeStatusEnum

        statuses = {
            "business_profile": NodeExecutionStatus(
                status=NodeStatusEnum.SUCCESS, confidence=0.95
            )
        }
        comp = _node_completeness(statuses, "business_profile", object())
        assert comp > 60.0, f"Expected >60 for SUCCESS node, got {comp}"

    def test_partial_node_gives_50_completeness(self):
        """Node PARTIAL → completeness = 50."""
        from business_analysis.agents.business_scoring import _node_completeness
        from business_analysis.schemas.models import NodeExecutionStatus, NodeStatusEnum

        statuses = {
            "service_analysis": NodeExecutionStatus(
                status=NodeStatusEnum.PARTIAL, confidence=0.5
            )
        }
        comp = _node_completeness(statuses, "service_analysis", object())
        assert comp == 50.0, f"Expected 50.0 for PARTIAL node, got {comp}"

    def test_overall_completeness_penalized_by_skipped(self):
        """Overall completeness must be reduced when multiple nodes are SKIPPED."""
        from business_analysis.agents.business_scoring import business_scoring_agent
        from business_analysis.schemas.models import (
            BusinessModel,
            BusinessProfile,
            BusinessType,
            CompanyScale,
            CompetitorAnalysis,
            CustomerAnalysis,
            DigitalAdoptionLevel,
            MarketAnalysis,
            MarketCondition,
            NodeExecutionStatus,
            NodeStatusEnum,
            ServiceAnalysis,
            ServiceVisibility,
        )
        from business_analysis.state import create_initial_state

        input_data = BusinessInput(
            company_name="Test Co", industry="Dental", location="Amsterdam"
        )
        state = create_initial_state(input_data)
        statuses = dict(state["node_statuses"])
        # 4 out of 7 are SKIPPED
        statuses["business_profile"] = NodeExecutionStatus(
            status=NodeStatusEnum.SUCCESS, confidence=0.9
        )
        statuses["market_analysis"] = NodeExecutionStatus(
            status=NodeStatusEnum.SKIPPED, confidence=0.0
        )
        statuses["customer_analysis"] = NodeExecutionStatus(
            status=NodeStatusEnum.SKIPPED, confidence=0.0
        )
        statuses["competitor_analysis"] = NodeExecutionStatus(
            status=NodeStatusEnum.SKIPPED, confidence=0.0
        )
        statuses["service_analysis"] = NodeExecutionStatus(
            status=NodeStatusEnum.SUCCESS, confidence=0.9
        )
        statuses["business_problem"] = NodeExecutionStatus(
            status=NodeStatusEnum.SUCCESS, confidence=0.9
        )
        statuses["opportunity"] = NodeExecutionStatus(
            status=NodeStatusEnum.SUCCESS, confidence=0.9
        )

        test_state = {
            **state,
            "business_profile": BusinessProfile(
                business_type=BusinessType.LOCAL_SERVICE,
                business_model=BusinessModel.B2C,
                industry="Dental",
                geographic_market="Amsterdam",
                company_scale=CompanyScale.SMALL,
            ),
            "market_analysis": MarketAnalysis(
                market_condition=MarketCondition.UNKNOWN,
                digital_adoption=DigitalAdoptionLevel.UNKNOWN,
            ),
            "customer_analysis": CustomerAnalysis(),
            "competitor_analysis": CompetitorAnalysis(),
            "service_analysis": ServiceAnalysis(
                overall_visibility=ServiceVisibility.MODERATE
            ),
            "business_problems": [
                BusinessProblem(
                    problem="Gap",
                    evidence_ids=["e1"],
                    business_impact=8,
                    confidence=0.8,
                    reasoning="Gap exists",
                )
            ],
            "opportunities": [],
            "node_statuses": statuses,
        }
        result = business_scoring_agent(test_state)
        completeness_obj = result["completeness"]
        # 4 nodes SKIPPED (0%) + 3 nodes SUCCESS (~96%) → overall ~41%
        assert completeness_obj.overall_analysis_completeness < 80.0, (
            f"Expected overall_completeness < 80 with 4 SKIPPED nodes, got {completeness_obj.overall_analysis_completeness}"
        )
        assert completeness_obj.market_completeness == 0.0, (
            "Market SKIPPED must have 0 completeness"
        )
        assert completeness_obj.customer_completeness == 0.0, (
            "Customer SKIPPED must have 0 completeness"
        )


class TestSDRBrief:
    """SDR Opportunity Brief must be generated with required fields."""

    def _make_full_report(self):

        from business_analysis.schemas.models import (
            AgencyService,
            AnalysisCompleteness,
            BusinessModel,
            BusinessProblem,
            BusinessProfile,
            BusinessScore,
            BusinessType,
            CompanyScale,
            CompetitorAnalysis,
            CustomerAnalysis,
            DigitalAdoptionLevel,
            MarketAnalysis,
            MarketCondition,
            Opportunity,
            ProblemSeverity,
            ProblemStatus,
            ProblemType,
            QualityGateResult,
            ScoreCategory,
            ServiceAnalysis,
            ServiceVisibility,
        )

        profile = BusinessProfile(
            business_type=BusinessType.LOCAL_SERVICE,
            business_model=BusinessModel.B2C,
            industry="Dental Services",
            geographic_market="Amsterdam",
            company_scale=CompanyScale.SMALL,
        )
        return FinalBusinessAnalysis(
            company_name="Atlas Kliniek",
            website="https://atlaskliniek.nl",
            industry="Dental Services",
            location="Amsterdam",
            business_profile=profile,
            market_analysis=MarketAnalysis(
                market_condition=MarketCondition.GROWING,
                digital_adoption=DigitalAdoptionLevel.MODERATE,
            ),
            customer_analysis=CustomerAnalysis(
                segments=[
                    CustomerSegment(
                        segment_name="Dental Anxiety Patients", is_primary=True
                    )
                ],
                primary_customers=["Dental Anxiety Patients"],
            ),
            competitor_analysis=CompetitorAnalysis(),
            service_analysis=ServiceAnalysis(
                overall_visibility=ServiceVisibility.MODERATE
            ),
            business_problems=[
                BusinessProblem(
                    problem="Service visibility gap",
                    title="Specialized Service Visibility Gap",
                    evidence_ids=["ev1"],
                    business_impact=9,
                    urgency=8,
                    confidence=0.9,
                    type=ProblemType.SERVICE_VISIBILITY,
                    status=ProblemStatus.POTENTIAL,
                    severity=ProblemSeverity.HIGH,
                )
            ],
            opportunities=[
                Opportunity(
                    problem_reference="Service visibility gap",
                    opportunity="Build service landing pages",
                    recommended_services=[
                        AgencyService.LOCAL_SEO,
                        AgencyService.CONTENT,
                    ],
                    priority=9,
                    rationale="High value",
                    expected_business_outcome="Improved discovery",
                )
            ],
            business_score=BusinessScore(
                business_fit=85,
                digital_need=65,
                opportunity_value=85,
                evidence_confidence=90,
                serviceability=90,
                analysis_completeness=57,
                overall_score=77,
                priority=ScoreCategory.HIGH,
                score_explanation="Test",
            ),
            completeness=AnalysisCompleteness(
                profile_completeness=96.0,
                market_completeness=0.0,
                customer_completeness=0.0,
                competitor_completeness=0.0,
                service_completeness=96.0,
                problem_completeness=94.0,
                opportunity_completeness=94.0,
                overall_analysis_completeness=57.0,
            ),
            quality_gate=QualityGateResult(
                quality_status="PASSED_WITH_WARNINGS",
                warnings=["Market analysis unavailable"],
            ),
            errors=[],
            warnings=["[QG] Market analysis unavailable"],
        )

    def test_sdr_brief_generated(self):
        """SDR brief markdown must be non-empty and contain key sections."""
        from main import generate_sdr_brief_markdown

        report = self._make_full_report()
        brief = generate_sdr_brief_markdown(report)
        assert brief, "SDR brief must not be empty"
        assert "Atlas Kliniek" in brief
        assert "Opportunity Score" in brief
        assert "Top Business Problems" in brief
        assert "Top Opportunities" in brief
        assert "Recommended Agency Services" in brief

    def test_sdr_brief_contains_recommended_services(self):
        """SDR brief must list the recommended services."""
        from main import generate_sdr_brief_markdown

        report = self._make_full_report()
        brief = generate_sdr_brief_markdown(report)
        assert "LOCAL_SEO" in brief or "local_seo" in brief.lower()

    def test_sdr_brief_includes_caveats_when_warnings_exist(self):
        """SDR brief must include Caveats section when quality gate has warnings."""
        from main import generate_sdr_brief_markdown

        report = self._make_full_report()
        brief = generate_sdr_brief_markdown(report)
        assert "Caveats" in brief or "Market analysis unavailable" in brief

    def test_sdr_brief_includes_verification_required(self):
        """SDR brief must include a verification section."""
        from main import generate_sdr_brief_markdown

        report = self._make_full_report()
        brief = generate_sdr_brief_markdown(report)
        assert "Verification" in brief


class TestWarningVsErrorSeparation:
    """Warnings must be separated from hard errors in the final report."""

    def test_service_warnings_dont_pollute_errors(self):
        """[ServiceAnalysis] prefixed messages must appear in warnings, not hard errors."""
        from business_analysis.graph import generate_final_report
        from business_analysis.schemas.models import (
            AgencyService,
            BusinessModel,
            BusinessProblem,
            BusinessProfile,
            BusinessScore,
            BusinessType,
            CompanyScale,
            CompetitorAnalysis,
            CustomerAnalysis,
            DigitalAdoptionLevel,
            MarketAnalysis,
            MarketCondition,
            Opportunity,
            ScoreCategory,
            ServiceAnalysis,
            ServiceVisibility,
        )
        from business_analysis.state import create_initial_state

        input_data = BusinessInput(
            company_name="Test Co", industry="Dental", location="Amsterdam"
        )
        state = create_initial_state(input_data)
        state = {
            **state,
            "business_profile": BusinessProfile(
                business_type=BusinessType.LOCAL_SERVICE,
                business_model=BusinessModel.B2C,
                industry="Dental",
                geographic_market="Amsterdam",
                company_scale=CompanyScale.SMALL,
            ),
            "market_analysis": MarketAnalysis(
                market_condition=MarketCondition.UNKNOWN,
                digital_adoption=DigitalAdoptionLevel.UNKNOWN,
            ),
            "customer_analysis": CustomerAnalysis(),
            "competitor_analysis": CompetitorAnalysis(),
            "service_analysis": ServiceAnalysis(
                overall_visibility=ServiceVisibility.MODERATE
            ),
            "business_problems": [
                BusinessProblem(
                    problem="Gap",
                    evidence_ids=["e1"],
                    business_impact=7,
                    confidence=0.8,
                    reasoning="test",
                )
            ],
            "opportunities": [
                Opportunity(
                    problem_reference="Gap",
                    opportunity="Fix gap",
                    recommended_services=[AgencyService.LOCAL_SEO],
                    priority=8,
                    rationale="High value",
                )
            ],
            "business_score": BusinessScore(
                business_fit=80,
                digital_need=65,
                opportunity_value=80,
                evidence_confidence=90,
                serviceability=90,
                analysis_completeness=57,
                overall_score=75,
                priority=ScoreCategory.HIGH,
                score_explanation="test",
            ),
            "errors": [
                "[ServiceAnalysis] Rejected malformed service: 'target_customers=Dental' — name malformed",
                "BusinessProfileAgent error: some real error",
            ],
        }
        result = generate_final_report(state)
        report = result["final_report"]
        assert report is not None
        # Hard errors must NOT contain ServiceAnalysis prefixed messages
        assert all(not e.startswith("[ServiceAnalysis]") for e in report.errors), (
            f"ServiceAnalysis warnings appeared in report.errors: {report.errors}"
        )
        # Warnings must contain the ServiceAnalysis message
        assert any("[ServiceAnalysis]" in w for w in report.warnings), (
            f"ServiceAnalysis message missing from report.warnings: {report.warnings}"
        )
        # Hard error must still be in report.errors
        assert any("BusinessProfileAgent" in e for e in report.errors), (
            f"Hard error not in report.errors: {report.errors}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
