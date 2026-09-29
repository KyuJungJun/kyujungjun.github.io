// Site-wide settings. Edit here.
export const site = {
  name: 'MINDS Lab',
  fullName: 'Materials Intelligence for Design and Simulations Lab',
  university: 'Korea University',
  university_ko: '고려대학교',
  pi_name: 'KyuJung Jun',
  pi_name_ko: '전규정',
  units: ['School of Mechanical Engineering', 'School of Smart Mobility'],
  units_ko: ['기계공학부', '스마트모빌리티학부'],
  email: 'kyujung@korea.ac.kr',
  office: '정운오 IT 교양관 709호',
  address_ko: '서울특별시 성북구 안암로 145 고려대학교 정운오 IT 교양관 709호',
  address_en: 'Room 709 (정운오 IT 교양관), Korea University, 145 Anam-ro, Seongbuk-gu, Seoul 02841, Korea',
  links: {
    scholar: 'https://scholar.google.com/citations?user=SmYXEicAAAAJ&hl=en',
    github: 'https://github.com/KyuJungJun',
    linkedin: 'https://www.linkedin.com/in/kyujung-jun',
    orcid: 'https://orcid.org/0000-0003-1974-028X',
  },
  // Recruiting popup shown on the front page. Set enabled: false to turn it off.
  popup: {
    enabled: true,
    title: '대학원생 · 학부연구생 모집',
    intro: 'MINDS Lab에서 머신러닝과 원자 단위 시뮬레이션으로 배터리 소재를 연구할 신입 대학원생(석사·박사)과 학부연구생을 모집합니다.',
    points: [
      'AI 기반 자율 소재 탐색, 고체전해질의 이온 전도 메커니즘, 머신러닝 원자간 퍼텐셜 등 연구 분야',
      '매주 지도교수 1:1 미팅, 다수의 CPU·GPU 계산 클러스터, MIT·UC Berkeley와의 공동연구',
      '기계공학부: 학부연구생·석사·박사 / 스마트모빌리티학부: 학부연구생 (면담 상시 가능)',
    ],
    closing: '연구실에 관심 있는 학생은 메일로 연락 바랍니다.',
    contact: '전규정 교수',
  },
  nav: [
    { href: '/research/', label: 'Research' },
    { href: '/people/', label: 'People' },
    { href: '/publications/', label: 'Publications' },
    { href: '/news/', label: 'News' },
    { href: '/teaching/', label: 'Teaching' },
    { href: '/recruiting/', label: 'Recruiting' },
  ],
};
