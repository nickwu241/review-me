class ReviewMeAPI {
    constructor() {
        this.API = 'http://localhost:5000'
    }

    notifications() {
        fetch(this.API + '/notifications').then((response) => {
            console.log(response)
        }).catch(err => {
            console.error(err)
        })
    }

    should_notify() {
        fetch(this.API + '/should_notify').then((response) => {
            console.log(response)
        }).catch(err => {
            console.error(err)
        })
    }

    issues(repos, callback) {
        fetch(this.API + '/issues?repos=' + repos.join(',')).then((response) => {
            let data = response.json()
            return data
        }).then(data => {
            callback(data)
        }).catch(err => {
            console.error(err)
        })
    }
}

export default ReviewMeAPI