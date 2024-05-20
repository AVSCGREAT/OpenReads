import team from '../../../templates/about/team.json';
export function initTeamFilter() {
    // Photos
    const default_profile_image =
    '../../../static/images/openlibrary-180x180.png';
    const bookUrlIcon = '../../../static/images/icons/icon_book-lg.png';
    const personalUrlIcon = '../../../static/images/globe-solid.svg';

    // Team sorted by last name
    const sortByLastName = (array) => {
        array.sort((a, b) => {
            const aName = a.name.split(' ');
            const bName = b.name.split(' ');
            const aLastName = aName[aName.length - 1];
            const bLastName = bName[bName.length - 1];
            if (aLastName < bLastName) {
                return -1;
            } else if (aLastName > bLastName) {
                return 1;
            } else {
                return 0;
            }
        });
    };
    sortByLastName(team);

    // Match a substring in each person's role
    const matchSubstring = (array, substring) => {
        return array.some((item) => item.includes(substring));
    };

    // *************************************** Team sorted by role ***************************************
    // ********** STAFF **********
    const staff = team.filter((person) => matchSubstring(person.roles, 'staff'));
    const staffEmeritus = staff.filter((person) =>
        matchSubstring(person.roles, 'emeritus')
    );
    const staffCurrent = staff.filter(
        (person) => !matchSubstring(person.roles, 'emeritus')
    );

    // ********** FELLOWS **********
    const fellows = team.filter(
        (person) =>
            matchSubstring(person.roles, 'fellow') &&
      !matchSubstring(person.roles, 'staff')
    );
    const currentFellows = fellows.filter((person) =>
        matchSubstring(person.roles, '2023')
    );
    const pastFellows = fellows.filter(
        (person) => !matchSubstring(person.roles, '2023')
    );

    // ********** VOLUNTEERS **********
    const volunteers = team.filter(
        (person) =>
            matchSubstring(person.roles, 'volunteer') &&
      !matchSubstring(person.roles, 'fellow')
    );

    // *************************************** Selectors and eventListeners ***************************************
    const roleFilter = document.getElementById('role');
    const departmentFilter = document.getElementById('department');
    roleFilter.addEventListener('change', (e) =>
        filterTeam(e.target.value, departmentFilter.value)
    );
    departmentFilter.addEventListener('change', (e) =>
        filterTeam(roleFilter.value, e.target.value)
    );
    // Example usage: update multiple parameters
    updateURLParameters({
        role: '',
        department: ''
    });
    const cardsContainer = document.querySelector('.teamCards_container');

    // *************************************** Functions ***************************************
    const showError = () => {
        const noResults = document.createElement('h3');
        noResults.classList = 'noResults';
        noResults.innerHTML =
      'It looks like we don\'t have anyone with those specifications.';
        cardsContainer.append(noResults);
    };

    const createCards = (array) => {
        array.map((member) => {
            // create
            const teamCardContainer = document.createElement('div');
            const teamCard = document.createElement('div');

            const teamCardPhotoContainer = document.createElement('div');
            const teamCardPhoto = document.createElement('img');

            const teamCardDescription = document.createElement('div');
            const memberOlLink = document.createElement('a');
            const memberName = document.createElement('h2');
            // const memberRole = document.createElement('h4');
            // const memberDepartment = document.createElement('h3');
            const memberTitle = document.createElement('h3');

            const descriptionLinks = document.createElement('div');

            //modify
            teamCardContainer.classList = 'teamCard__container';
            teamCard.classList = 'teamCard';

            teamCardPhotoContainer.classList = 'teamCard__photoContainer';
            teamCardPhoto.classList = 'teamCard__photo';
            teamCardPhoto.src = `${
                member.photo_path ? member.photo_path : default_profile_image
            }`;

            teamCardDescription.classList.add('teamCard__description');
            if (member.ol_key) {
                memberOlLink.href = `https://openlibrary.org/people/${member.ol_key}`;
            }
            member.name.length >= 18
                ? (memberName.classList = 'description__name--length-long')
                : (memberName.classList = 'description__name--length-short');

            memberName.innerHTML = `${member.name}`;
            // memberRole.classList = 'description__role';
            // memberRole.innerHTML = `${role}`;
            // memberDepartment.classList = 'description__department';
            // memberDepartment.innerHTML = `${member.departments}`;
            memberTitle.classList = 'description__title';
            memberTitle.innerHTML = `${member.title}`;

            descriptionLinks.classList = 'description__links';
            if (member.personal_url) {
                const memberPersonalA = document.createElement('a');
                const memberPersonalImg = document.createElement('img');

                memberPersonalA.href = `${member.personal_url}`;
                memberPersonalImg.src = personalUrlIcon;
                memberPersonalImg.classList = 'links__site';

                memberPersonalA.append(memberPersonalImg);
                descriptionLinks.append(memberPersonalA);
            }

            if (member.favorite_book_url) {
                const memberBookA = document.createElement('a');
                const memberBookImg = document.createElement('img');

                memberBookA.href = `${member.favorite_book_url}`;
                memberBookImg.src = bookUrlIcon;
                memberBookImg.classList = 'links__book';

                memberBookA.append(memberBookImg);
                descriptionLinks.append(memberBookA);
            }

            // append
            teamCardPhotoContainer.append(teamCardPhoto);
            memberOlLink.append(memberName);
            teamCardDescription.append(
                memberOlLink,
                // memberRole,
                // memberDepartment,
                memberTitle,
                descriptionLinks
            );
            teamCard.append(teamCardPhotoContainer, teamCardDescription);
            teamCardContainer.append(teamCard);
            cardsContainer.append(teamCardContainer);
        });
    };

    const createSectionHeading = (text) => {
        const sectionSeparator = document.createElement('div');
        sectionSeparator.innerHTML = `${text}`;
        sectionSeparator.classList = 'sectionSeparator';
        cardsContainer.append(sectionSeparator);
    };

    const createsubSection = (array, text) => {
        const subsectionSeparator = document.createElement('div');
        subsectionSeparator.innerHTML = `${text}`;
        subsectionSeparator.classList = 'subsectionSeparator';
        cardsContainer.append(subsectionSeparator);
        createCards(array);
    };

    const filterTeam = (role, department) => {
        cardsContainer.innerHTML = '';
        // **************************************** default sort *****************************************
        if (role === 'All' && department === 'All') {
            createSectionHeading('Staff');
            createsubSection(staffCurrent, 'Current');
            createsubSection(staffEmeritus, 'Emeritus');

            createSectionHeading('Fellows');
            createsubSection(currentFellows, 'Current');
            createsubSection(pastFellows, 'Past');

            createSectionHeading('Volunteers');
            createCards(volunteers);
        }
        // ************************************* sort by department ***************************************
        else if (role === 'All' && department !== 'All') {
            role = '';
            const filteredTeam = team.filter(
                (person) =>
                    matchSubstring(person.roles, role) &&
          matchSubstring(person.departments, department)
            );

            const staff = filteredTeam.filter((person) =>
                matchSubstring(person.roles, 'staff')
            );
            const staffEmeritus = staff.filter((person) =>
                matchSubstring(person.roles, 'emeritus')
            );
            const staffCurrent = staff.filter(
                (person) => !matchSubstring(person.roles, 'emeritus')
            );

            const fellows = filteredTeam.filter(
                (person) =>
                    matchSubstring(person.roles, 'fellow') &&
          !matchSubstring(person.roles, 'staff')
            );
            const currentFellows = fellows.filter((person) =>
                matchSubstring(person.roles, '2023')
            );
            const pastFellows = fellows.filter(
                (person) => !matchSubstring(person.roles, '2023')
            );

            const volunteers = filteredTeam.filter(
                (person) =>
                    matchSubstring(person.roles, 'volunteer') &&
          !matchSubstring(person.roles, 'fellow')
            );

            staff.length && createSectionHeading('Staff');
            staffCurrent.length && createsubSection(staffCurrent, 'Current');
            staffEmeritus.length && createsubSection(staffEmeritus, 'Emeritus');

            fellows.length && createSectionHeading('Fellows');
            currentFellows.length && createsubSection(currentFellows, 'Current');
            pastFellows.length && createsubSection(pastFellows, 'Past');

            volunteers.length && createSectionHeading('Volunteers');
            createCards(volunteers);
        }
        // ****************************** sort by role and/or department *******************************
        else {
            department === 'All' ? (department = '') : department;
            createSectionHeading(capitalize(role));
            if (role === 'volunteer') {
                const filteredVolunteers = volunteers.filter((person) =>
                    matchSubstring(person.departments, department)
                );
                filteredVolunteers.length !== 0
                    ? createCards(filteredVolunteers)
                    : showError();
            } else if (role === 'staff') {
                const filteredCurrentStaff = staffCurrent.filter((person) =>
                    matchSubstring(person.departments, department)
                );
                const filteredStaffEmeritus = staffEmeritus.filter((person) =>
                    matchSubstring(person.departments, department)
                );
                filteredCurrentStaff.length &&
          createsubSection(filteredCurrentStaff, 'Current');
                filteredStaffEmeritus.length &&
          createsubSection(filteredStaffEmeritus, 'Emeritus');
                !filteredCurrentStaff.length &&
          !filteredStaffEmeritus.length &&
          showError();
            } else {
                const filteredCurrentFellows = currentFellows.filter((person) =>
                    matchSubstring(person.departments, department)
                );
                const filteredPastFellows = pastFellows.filter((person) =>
                    matchSubstring(person.departments, department)
                );
                filteredCurrentFellows.length &&
          createsubSection(filteredCurrentFellows, 'Current');
                filteredPastFellows.length &&
          createsubSection(filteredPastFellows, 'Past');
                !filteredCurrentFellows.length &&
          !filteredPastFellows.length &&
          showError();
            }
        }
    };

    const capitalize = (text) => {
        const firstLetter = text[0].toUpperCase();
        if (text === 'fellow' || text === 'volunteer') {
            return `${firstLetter + text.slice(1)}s`;
        } else {
            return firstLetter + text.slice(1);
        }
    };

    // on page load
    createSectionHeading('Staff');
    createsubSection(staffCurrent, 'Current');
    createsubSection(staffEmeritus, 'Emeritus');

    createSectionHeading('Fellows');
    createsubSection(currentFellows, 'Current');
    createsubSection(pastFellows, 'Past');

    createSectionHeading('Volunteers');
    createCards(volunteers);
}
