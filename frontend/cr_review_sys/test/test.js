var expect = require('chai').expect;

describe('test mocha and chai', function() {
  it('1 add 1 should be 2', function() {
    expect(1+1).to.be.equal(2);
  });
});