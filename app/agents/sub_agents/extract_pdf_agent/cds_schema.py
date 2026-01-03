from pydantic import BaseModel, Field
from typing import List, Optional

# --- 1. 하위 구조 (Sub-structures) 정의 ---

class GenderStats(BaseModel):
    """지원자 및 합격자 성별 통계"""
    total: Optional[int] = Field(None, description="총 인원")
    men: Optional[int] = Field(None, description="남성 인원")
    women: Optional[int] = Field(None, description="여성 인원")
    another_gender: Optional[int] = Field(None, description="Another Gender 인원 (CDS C1 섹션 참조, 데이터가 있으면 필수 기입)")
    unknown_gender: Optional[int] = Field(None, description="성별 미상 인원")

class EnrollmentStats(BaseModel):
    """등록(Enrollment) 통계"""
    total: Optional[int] = Field(None, description="총 등록 인원")
    full_time: Optional[int] = Field(None, description="Full-time 등록 인원")
    part_time: Optional[int] = Field(None, description="Part-time 등록 인원")

class WaitlistStats(BaseModel):
    """대기자 명단(Waitlist) 통계"""
    has_policy: Optional[bool] = Field(None, description="대기자 명단 운영 여부 (True/False)")
    offered_spot: Optional[int] = Field(None, description="웨이팅 제안을 받은 학생 수")
    accepted_spot: Optional[int] = Field(None, description="웨이팅을 수락한 학생 수")
    admitted_from_waitlist: Optional[int] = Field(None, description="웨이팅에서 실제로 합격한 학생 수")

class SatScores(BaseModel):
    """SAT 점수 분포 (CDS C9)"""
    composite_25th: Optional[int] = Field(None, description="Composite 25th percentile")
    composite_50th: Optional[int] = Field(None, description="Composite 50th percentile (Median)")
    composite_75th: Optional[int] = Field(None, description="Composite 75th percentile")
    ebrw_25th: Optional[int] = Field(None, description="EBRW 25th percentile")
    ebrw_75th: Optional[int] = Field(None, description="EBRW 75th percentile")
    math_25th: Optional[int] = Field(None, description="Math 25th percentile")
    math_75th: Optional[int] = Field(None, description="Math 75th percentile")

class ActScores(BaseModel):
    """ACT 점수 분포 (CDS C9)"""
    composite_25th: Optional[int] = Field(None, description="Composite 25th percentile")
    composite_50th: Optional[int] = Field(None, description="Composite 50th percentile")
    composite_75th: Optional[int] = Field(None, description="Composite 75th percentile")
    math_25th: Optional[int] = Field(None, description="Math 25th percentile")
    math_75th: Optional[int] = Field(None, description="Math 75th percentile")
    english_25th: Optional[int] = Field(None, description="English 25th percentile")
    english_75th: Optional[int] = Field(None, description="English 75th percentile")

class Expenses(BaseModel):
    """학비 및 비용 (CDS G1)"""
    tuition_in_state: Optional[int] = Field(None, description="주 거주민 학비 (사립대의 경우 공통 학비)")
    tuition_out_of_state: Optional[int] = Field(None, description="타 주 거주민 학비 (사립대는 in_state와 동일하거나 null)")
    fees: Optional[int] = Field(None, description="필수 수수료 (Required Fees)")
    room_and_board: Optional[int] = Field(None, description="기숙사 및 식비")
    books_and_supplies: Optional[int] = Field(None, description="교재 및 준비물 비용")
    other_expenses: Optional[int] = Field(None, description="기타 비용")

class FinancialAidStats(BaseModel):
    """재정 보조 통계 (CDS H1, H6)"""
    international_students_eligible: Optional[bool] = Field(None, description="유학생 재정 보조 가능 여부 (CDS H6)")
    average_need_based_package: Optional[int] = Field(None, description="평균 Need-based 장학금 패키지 금액")
    percent_need_met: Optional[str] = Field(None, description="재정 필요 충족률 (예: '100%')")

class Demographics(BaseModel):
    """학생 구성 통계"""
    out_of_state_percent: Optional[str] = Field(None, description="타 주 학생 비율 (CDS F1)")
    international_percent: Optional[str] = Field(None, description="유학생 비율")

class DeadlineDetail(BaseModel):
    """지원 마감일 상세"""
    deadline: Optional[str] = Field(None, description="마감일 (MM-DD 형식)")
    notification_date: Optional[str] = Field(None, description="합격 발표일")
    is_binding: Optional[bool] = Field(None, description="합격 시 등록 의무 여부")
    type: Optional[str] = Field(None, description="전형 타입 (예: Early Action, RESTRICTED Early Action 등)")

class TransferAdmission(BaseModel):
    """편입학 정보"""
    deadline: Optional[str] = Field(None, description="편입 지원 마감일")
    is_rolling: Optional[bool] = Field(None, description="Rolling Admission 여부")


# --- 2. 주요 섹션 (Main Sections) 정의 ---

class Metadata(BaseModel):
    source_file: Optional[str] = Field(None, description="소스 PDF 파일명")
    academic_year: Optional[str] = Field(None, description="CDS 학년도 (예: 2024-2025)")
    extraction_date: Optional[str] = Field(None, description="추출 날짜 (YYYY-MM-DD)")

class GeneralInfo(BaseModel):
    institution_name: Optional[str] = Field(None, description="학교 공식 명칭")
    school_type: Optional[str] = Field(None, description="'Private' 또는 'Public' (CDS A2)")
    school_category: Optional[str] = Field(None, description="'University' 또는 'Liberal Arts College'")
    academic_calendar: Optional[str] = Field(None, description="'Semester', 'Quarter', 'Trimester' 등 (CDS A4)")
    website: Optional[str] = Field(None, description="학교 홈페이지 URL")
    city: Optional[str] = Field(None, description="도시")
    state: Optional[str] = Field(None, description="주 (State)")

class AdmissionFactors(BaseModel):
    """CDS C7 섹션: 입학 사정 요소"""
    very_important: List[str] = Field(default_factory=list, description="Very Important 요소들")
    important: List[str] = Field(default_factory=list, description="Important 요소들")
    considered: List[str] = Field(default_factory=list, description="Considered 요소들 (Interview 포함 여부 확인)")
    not_considered: List[str] = Field(default_factory=list, description="Not Considered 요소들")

class AdmissionsStatistics(BaseModel):
    cohort_year: Optional[str] = Field(None, description="입학 연도 (예: Fall 2024)")
    acceptance_rate: Optional[float] = Field(None, description="합격률 (%)")
    yield_rate: Optional[float] = Field(None, description="등록률 (%)")
    applicants: GenderStats
    admitted: GenderStats
    enrolled: EnrollmentStats
    waitlist: WaitlistStats

class TestScores(BaseModel):
    policy: Optional[str] = Field(None, description="'Test Optional', 'Test Required', 'Test Blind' 등 (CDS C8)")
    submission_rate_sat: Optional[str] = Field(None, description="SAT 제출 비율")
    submission_rate_act: Optional[str] = Field(None, description="ACT 제출 비율")
    sat: SatScores
    act: ActScores

class HighSchoolProfile(BaseModel):
    average_gpa: Optional[float] = Field(None, description="평균 GPA (4.0 만점 기준)")
    gpa_submission_rate: Optional[str] = Field(None, description="GPA 제출 비율")
    class_rank_submission_rate: Optional[str] = Field(None, description="석차 제출 비율")
    percent_top_10: Optional[str] = Field(None, description="상위 10% 비율")
    percent_top_25: Optional[str] = Field(None, description="상위 25% 비율")
    percent_top_50: Optional[str] = Field(None, description="상위 50% 비율")

class CostAndFinancialAid(BaseModel):
    tuition_structure: Optional[str] = Field(None, description="'Unified' (사립) 또는 'Dual' (주립)")
    expenses: Expenses
    financial_aid: FinancialAidStats

class StudentLifeAndFaculty(BaseModel):
    student_faculty_ratio: Optional[str] = Field(None, description="학생 대 교수 비율 (예: 5:1)")
    undergraduate_enrollment: Optional[int] = Field(None, description="학부 총원")
    demographics: Demographics
    class_size_under_20_percent: Optional[str] = Field(None, description="20명 미만 수업 비율 (CDS I-3)")

class Deadlines(BaseModel):
    early_decision_1: Optional[DeadlineDetail] = None
    early_decision_2: Optional[DeadlineDetail] = None
    early_action: Optional[DeadlineDetail] = None
    regular_decision: Optional[DeadlineDetail] = None
    transfer_admission: Optional[TransferAdmission] = None


# --- 3. 최상위 루트 모델 (Root Schema) ---

class UniversityDataSchema(BaseModel):
    """
    미국 대학 Common Data Set (CDS) 정보 추출을 위한 통합 스키마 (V2)
    """
    metadata: Metadata
    general_info: GeneralInfo
    admission_factors: AdmissionFactors
    admissions_statistics: AdmissionsStatistics
    test_scores: TestScores
    high_school_profile: HighSchoolProfile
    cost_and_financial_aid: CostAndFinancialAid
    student_life_and_faculty: StudentLifeAndFaculty
    deadlines: Deadlines