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
  address_en: 'Jung Woonoh IT & General Education Center #709, Korea University, 145 Anam-ro, Seongbuk-gu, Seoul, 02841, Republic of Korea',
  links: {
    scholar: 'https://scholar.google.com/citations?user=SmYXEicAAAAJ&hl=en',
    github: 'https://github.com/KyuJungJun',
    linkedin: 'https://www.linkedin.com/in/kyujung-jun',
    orcid: 'https://orcid.org/0000-0003-1974-028X',
  },
  // Recruiting popup shown on the front page. Set enabled: false to turn it off.
  popup: {
    enabled: true,
    title: '대학원생 · 학부연구생 · 방문연구생 모집',
    intro: 'MINDS Lab에서 머신러닝과 원자 단위 시뮬레이션으로 배터리 소재를 연구할 신입 대학원생(석사·박사), 학부연구생, 방문연구생, 박사후연구원을 모집합니다.',
    points: [
      'AI 기반 자율 소재 탐색, 머신러닝 원자간 퍼텐셜, 고체전해질의 이온 전도 메커니즘 등 연구 분야',
      '그룹 미팅 및 지도교수와의 1:1 연구 미팅, 다수의 CPU·GPU 계산 클러스터, 해외 대학 연구실과의 공동연구',
      '기계공학, 신소재공학, 화학공학, 물리학, 화학, 에너지공학 등 다양한 전공 환영',
    ],
    closing: '관심 있는 학생은 부담 없이 메일로 연락 주세요.',
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
